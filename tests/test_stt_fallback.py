from unittest.mock import MagicMock, patch
import pytest
from services.stt_service import STTService
from config import settings


def test_stt_fallback_to_cpu_on_cuda_failure():
    # Create a new instance of STTService to avoid caching
    service = STTService()

    # Save original settings to restore later
    original_device = settings.whisper_device
    original_compute_type = settings.whisper_compute_type
    original_model_size = settings.whisper_model_size

    # Force settings to use CUDA and float16
    settings.whisper_device = "cuda"
    settings.whisper_compute_type = "float16"
    settings.whisper_model_size = "tiny"

    # Mock WhisperModel constructor
    with patch("services.stt_service.WhisperModel") as mock_whisper:
        # First call (cuda) raises an Exception, second call (cpu) succeeds
        def side_effect(model_size, device, compute_type):
            if device == "cuda":
                raise RuntimeError("CUDA out of memory or not supported")
            # Return a dummy mock object for CPU
            mock_instance = MagicMock()
            mock_instance.device = device
            mock_instance.compute_type = compute_type
            return mock_instance

        mock_whisper.side_effect = side_effect

        # Call get_model
        model = service._get_model()

        # Assertions
        assert model is not None
        assert mock_whisper.call_count == 2

        # Check first call arguments (CUDA)
        mock_whisper.assert_any_call("tiny", device="cuda", compute_type="float16")
        # Check second call arguments (CPU fallback)
        mock_whisper.assert_any_call("tiny", device="cpu", compute_type="int8")

    # Restore settings
    settings.whisper_device = original_device
    settings.whisper_compute_type = original_compute_type
    settings.whisper_model_size = original_model_size
