"""
Test script to verify VRM loader functionality.
"""
import sys
import os
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_vrm_loader():
    """Test loading a VRM file."""
    try:
        # Import the VRM loader
        from avatarmcp.models.vrm_loader import VRMLoader
        
        # Path to test VRM file
        vrm_path = Path("D:/Dev/repos/avatarmcp/examples/Nekomimi-chan.vrm")
        
        if not vrm_path.exists():
            logger.error(f"VRM file not found at {vrm_path}")
            return False
            
        logger.info(f"Loading VRM file: {vrm_path}")
        
        # Try to load the VRM file
        try:
            vrm_loader = VRMLoader()
            vrm_model = vrm_loader.load(vrm_path)
            
            if vrm_model:
                logger.info("✅ VRM file loaded successfully!")
                logger.info(f"Model ID: {vrm_model.model_id}")
                logger.info(f"Number of meshes: {len(vrm_model.meshes) if hasattr(vrm_model, 'meshes') else 0}")
                return True
            else:
                logger.error("❌ Failed to load VRM file")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error loading VRM file: {str(e)}", exc_info=True)
            return False
            
    except ImportError as e:
        logger.error(f"❌ Failed to import VRM loader: {str(e)}")
        return False

if __name__ == "__main__":
    # Add the project root to Python path
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_root)
    
    # Run the test
    success = test_vrm_loader()
    sys.exit(0 if success else 1)
