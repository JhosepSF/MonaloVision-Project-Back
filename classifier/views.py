import os
import time
import base64
import logging
import cv2
import numpy as np
import torch
import torchvision.transforms as T
from PIL import Image
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from torchvision import transforms

# Import our singleton model manager
from classifier.model_loader import ModelManager

logger = logging.getLogger(__name__)

@csrf_exempt
@require_POST
def classify_cocoa(request):
    """
    Main API endpoint to classify a cocoa pod image.
    Steps:
      1. Receives an image from the POST request.
      2. Segments the cocoa pod using Mask R-CNN.
      3. Rotates the segmented image 90 degrees clockwise (matching training setup).
      4. Extracts features using fine-tuned ViT-Tiny.
      5. Predicts cocoa health stage using scikit-learn SVM.
      6. Returns JSON results with predictions, confidence, probabilities, and the base64-encoded segmented image.
    """
    start_time = time.time()
    
    # 1. Validate request
    if 'image' not in request.FILES:
        return JsonResponse({
            'error': 'No image file was uploaded. Please send a POST request with the file under key "image".'
        }, status=400)
        
    image_file = request.FILES['image']
    
    try:
        # Load the uploaded image with Pillow
        image = Image.open(image_file).convert("RGB")
        original_np = np.array(image)
    except Exception as e:
        logger.error(f"Error loading image: {str(e)}")
        return JsonResponse({
            'error': f'Invalid image file: {str(e)}'
        }, status=400)

    # 2. Get singleton models
    try:
        manager = ModelManager.get_instance()
        device = manager.device
    except Exception as e:
        logger.error(f"Error initializing models: {str(e)}")
        return JsonResponse({
            'error': f'Failed to load classification models on backend: {str(e)}'
        }, status=500)

    segmentation_success = False
    segmented_image = None

    # 3. Perform Segmentation with Mask R-CNN
    try:
        # Transform for Mask R-CNN
        transform = T.Compose([T.ToTensor()])
        img_tensor = transform(image).to(device)
        
        with torch.no_grad():
            prediction = manager.mask_rcnn([img_tensor])
            
        masks = prediction[0]['masks']
        
        if masks.shape[0] > 0:
            # We found objects, let's select the one closest to the center
            height, width = original_np.shape[:2]
            img_center = np.array([width // 2, height // 2])

            min_dist = float('inf')
            best_mask = None

            for mask in masks:
                # Convert PyTorch float mask to binary numpy mask
                binary = (mask.squeeze() > 0.5).cpu().numpy().astype(np.uint8)

                contours, _ = cv2.findContours(
                    binary,
                    cv2.RETR_EXTERNAL,
                    cv2.CHAIN_APPROX_SIMPLE
                )

                if contours:
                    largest_contour = max(contours, key=cv2.contourArea)
                    M = cv2.moments(largest_contour)

                    if M["m00"] != 0:
                        cx = int(M["m10"] / M["m00"])
                        cy = int(M["m01"] / M["m00"])

                        obj_center = np.array([cx, cy])
                        dist = np.linalg.norm(img_center - obj_center)

                        if dist < min_dist:
                            min_dist = dist
                            best_mask = binary

            if best_mask is not None:
                # Apply morphological cleanup
                kernel = np.ones((5, 5), np.uint8)
                binary_mask = cv2.morphologyEx(best_mask, cv2.MORPH_CLOSE, kernel)

                # Ensure mask is exactly the same size as original image
                if binary_mask.shape != original_np.shape[:2]:
                    binary_mask = cv2.resize(
                        binary_mask,
                        (original_np.shape[1], original_np.shape[0]),
                        interpolation=cv2.INTER_NEAREST
                    )

                # Segment cocoa pod on black background
                binary_mask_3 = np.stack([binary_mask] * 3, axis=-1)
                black_background = np.zeros_like(original_np, dtype=np.uint8)
                segmented_image = np.where(binary_mask_3 == 1, original_np, black_background)
                segmentation_success = True
                
    except Exception as e:
        logger.warning(f"Mask R-CNN segmentation encountered an error: {str(e)}. Proceeding without segmentation.")

    # 4. Determine which image to feed to ViT-Tiny
    if segmentation_success and segmented_image is not None:
        image_to_process = segmented_image
    else:
        logger.info("Segmentation skipped or failed. Using raw image as fallback.")
        image_to_process = original_np

    # 5. Rotate 90 degrees clockwise (matching training preprocessing)
    try:
        processed_rotated = cv2.rotate(
            image_to_process,
            cv2.ROTATE_90_CLOCKWISE
        )
    except Exception as e:
        logger.error(f"Failed to rotate image: {str(e)}")
        processed_rotated = image_to_process

    # 6. Preprocess for ViT-Tiny Extractor
    try:
        processed_pil = Image.fromarray(processed_rotated)
        
        # Replicate eval_transforms from training
        eval_transforms = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406],
                                 [0.229, 0.224, 0.225])
        ])
        
        vit_input = eval_transforms(processed_pil).unsqueeze(0).to(device)
        
        # 7. Extract features with ViT-Tiny
        with torch.no_grad():
            features = manager.extractor(vit_input)
            features_np = features.cpu().numpy().astype(np.float32)
            
        # 8. Classify with SVM pipeline (includes StandardScaler)
        pred_class_idx = int(manager.svm.predict(features_np)[0])
        probs = manager.svm.predict_proba(features_np)[0]
        
    except Exception as e:
        logger.error(f"Inference pipeline encountered an error: {str(e)}")
        return JsonResponse({
            'error': f'Failed to run model inference: {str(e)}'
        }, status=500)

    # 9. Format response
    predicted_class_name = manager.class_names[pred_class_idx]
    confidence = float(probs[pred_class_idx])
    
    probabilities_dict = {}
    for idx, name in enumerate(manager.class_names):
        probabilities_dict[name] = float(probs[idx])
        
    # Generate Base64 segmented image for premium frontend rendering
    try:
        # Convert RGB to BGR for cv2 encoding
        processed_bgr = cv2.cvtColor(processed_rotated, cv2.COLOR_RGB2BGR)
        _, buffer = cv2.imencode('.jpg', processed_bgr)
        segmented_base64 = base64.b64encode(buffer).decode('utf-8')
    except Exception as e:
        logger.warning(f"Could not encode segmented image to base64: {str(e)}")
        segmented_base64 = None

    elapsed_time_ms = int((time.time() - start_time) * 1000)

    response_data = {
        'class': predicted_class_name,
        'confidence': confidence,
        'probabilities': probabilities_dict,
        'segmentation_success': segmentation_success,
        'segmented_image': segmented_base64,
        'latency_ms': elapsed_time_ms
    }

    return JsonResponse(response_data)
