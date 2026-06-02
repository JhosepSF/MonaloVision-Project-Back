import os
import sys
import base64
import json
import requests

def test_cocoa_classifier(image_path, api_url="http://127.0.0.1:8000/api/classify/"):
    print("=" * 60)
    print("[TEST] Testing Cocoa Pod Disease Classifier Django API")
    print("=" * 60)
    
    if not os.path.exists(image_path):
        print(f"[ERROR] Image file not found at: {image_path}")
        return
        
    print(f"[FILE] Selected input image: {image_path} ({os.path.getsize(image_path)} bytes)")
    print(f"[URL] Sending POST request to: {api_url}")
    
    # Open the image file in binary mode
    try:
        with open(image_path, "rb") as f:
            files = {"image": (os.path.basename(image_path), f, "image/jpeg")}
            
            print("[WAIT] Awaiting server response (Mask R-CNN + ViT + SVM inference)...")
            response = requests.post(api_url, files=files)
            
    except requests.exceptions.ConnectionError:
        print("[ERROR] Could not connect to the Django server. Is it running?")
        print("[TIP] Run: python manage.py runserver 8000")
        return
    except Exception as e:
        print(f"[ERROR] Error during request: {e}")
        return

    print(f"[STATUS] Response status code: {response.status_code}")
    
    try:
        data = response.json()
    except Exception as e:
        print("[ERROR] Response was not valid JSON.")
        print(f"Raw response content: {response.text[:500]}")
        return

    if response.status_code != 200:
        print("[ERROR] Error returned by API:")
        print(json.dumps(data, indent=4, ensure_ascii=False))
        return

    # Print classification results
    import unicodedata
    predicted_class = data.get('class', '')
    clean_predicted_class = unicodedata.normalize('NFC', predicted_class)
    try:
        clean_predicted_class.encode(sys.stdout.encoding or 'cp1252')
    except UnicodeEncodeError:
        clean_predicted_class = clean_predicted_class.replace('ñ', 'n').replace('̃', '')

    print("\n[SUCCESS] Classification Successful!")
    print("-" * 40)
    print(f"Predicted Class : {clean_predicted_class}")
    print(f"Confidence      : {data.get('confidence') * 100:.2f}%")
    print(f"Segmentation OK : {data.get('segmentation_success')}")
    print(f"Latency         : {data.get('latency_ms')} ms")
    print("-" * 40)
    
    print("\n[METRICS] Probabilities for each class:")
    import unicodedata
    for cls, prob in data.get("probabilities", {}).items():
        # Normalize combining tilde \u0303 + n to standard ñ
        clean_cls = unicodedata.normalize('NFC', cls)
        try:
            # Test if console can print it
            clean_cls.encode(sys.stdout.encoding or 'cp1252')
        except UnicodeEncodeError:
            # Fallback to plain English chars
            clean_cls = clean_cls.replace('ñ', 'n').replace('̃', '')
        print(f"  * {clean_cls:15}: {prob * 100:6.2f}%")
        
    # Save the base64-encoded segmented image
    segmented_b64 = data.get("segmented_image")
    if segmented_b64:
        output_file = "debug_segmented.jpg"
        try:
            image_data = base64.b64decode(segmented_b64)
            with open(output_file, "wb") as fh:
                fh.write(image_data)
            print(f"\n[IMAGE] Segmented image successfully saved to: {os.path.abspath(output_file)}")
            print("[TIP] You can open this image to inspect the Mask R-CNN segmentation and 90° clockwise rotation.")
        except Exception as e:
            print(f"[WARNING] Could not decode and save segmented image: {e}")
    else:
        print("\n[WARNING] No segmented image was returned in the response.")

if __name__ == "__main__":
    # Default to Front/assets/1.jpeg if it exists, otherwise allow command line arg
    default_img = os.path.join("..", "Front", "assets", "1.jpeg")
    
    img_path = sys.argv[1] if len(sys.argv) > 1 else default_img
    test_cocoa_classifier(img_path)
