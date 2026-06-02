import os
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
import logging
import threading
import torch
import torch.nn as nn
import timm
import torchvision
import joblib
from django.conf import settings

logger = logging.getLogger(__name__)

# Replicate the ViTFeatureExtractor class structure from the training script
class ViTFeatureExtractor(nn.Module):
    """
    Final feature extractor class.
    Loads the fine-tuned ViT-Tiny model and outputs average-pooled feature vectors.
    """
    def __init__(self, vit_name, vit_state_dict):
        super().__init__()
        self.vit = timm.create_model(
            vit_name,
            pretrained=False,
            num_classes=0,
            global_pool="avg"
        )
        self.vit.load_state_dict(vit_state_dict, strict=True)
        self.feature_dim = self.vit.num_features

    def forward(self, x):
        return self.vit(x)


class ModelManager:
    """
    Thread-safe Singleton class to load and keep all classification and segmentation models in memory.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(ModelManager, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        with self._lock:
            if self._initialized:
                return

            logger.info("Initializing ModelManager and loading models...")
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            logger.info(f"ModelManager is using device: {self.device}")

            # Define paths relative to the classifier application directory
            models_dir = os.path.join(os.path.dirname(__file__), "modelos")

            vit_state_dict_path = os.path.join(
                models_dir, "vit_tiny_extractor_finetuned_vittiny_svm_state_dict.pth"
            )
            svm_classifier_path = os.path.join(
                models_dir, "final_svm_classifier_vittiny_svm.pkl"
            )

            # 1. Load Mask R-CNN for segmentation
            logger.info("Loading Mask R-CNN ResNet-50 FPN for cacao segmentation...")
            try:
                from torchvision.models.detection import MaskRCNN_ResNet50_FPN_Weights
                self.mask_rcnn = torchvision.models.detection.maskrcnn_resnet50_fpn(
                    weights=MaskRCNN_ResNet50_FPN_Weights.DEFAULT
                )
            except (ImportError, AttributeError):
                # Fallback for older torchvision versions
                self.mask_rcnn = torchvision.models.detection.maskrcnn_resnet50_fpn(
                    pretrained=True
                )
            
            self.mask_rcnn.to(self.device)
            self.mask_rcnn.eval()
            logger.info("Mask R-CNN loaded successfully.")

            # 2. Load ViT-Tiny Extractor
            logger.info(f"Loading ViT-Tiny state dict from: {vit_state_dict_path}")
            if not os.path.exists(vit_state_dict_path):
                raise FileNotFoundError(f"ViT state dict not found at {vit_state_dict_path}")

            # Load the state dict (safe loading)
            try:
                state_dict = torch.load(vit_state_dict_path, map_location=self.device, weights_only=False)
            except TypeError:
                state_dict = torch.load(vit_state_dict_path, map_location=self.device)

            VIT_MODEL_NAME = "vit_tiny_patch16_224.augreg_in21k"
            self.extractor = ViTFeatureExtractor(
                vit_name=VIT_MODEL_NAME,
                vit_state_dict=state_dict
            )
            self.extractor.to(self.device)
            self.extractor.eval()
            # Freeze all parameters
            for p in self.extractor.parameters():
                p.requires_grad = False
            logger.info("ViT-Tiny Feature Extractor loaded successfully.")

            # 3. Load SVM Classifier Pipeline (StandardScaler + SVC)
            logger.info(f"Loading SVM Classifier from: {svm_classifier_path}")
            if not os.path.exists(svm_classifier_path):
                raise FileNotFoundError(f"SVM model not found at {svm_classifier_path}")

            self.svm = joblib.load(svm_classifier_path)
            logger.info("SVM Classifier Pipeline loaded successfully.")

            # Define classes as found in model config
            self.class_names = ["DañoLigero", "DañoModerado", "DañoSevero", "Sana"]

            self._initialized = True
            logger.info("ModelManager fully initialized and all models loaded.")

    @classmethod
    def get_instance(cls):
        """
        Global access point to the singleton instance.
        """
        return cls()
