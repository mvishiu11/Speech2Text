def is_chunk_ready(buffer: bytearray, 
                   sample_rate: int = 16000, 
                   bit_depth: int = 16, 
                   channels: int = 1, 
                   seconds: int = 20,
                   byte_mode: bool = False,
                   bytes: int = 16000) -> bool:
    """
    Check if the buffer has enough data for a 20-second audio chunk.

    Args:
    buffer (bytearray): The buffer containing the audio data.
    sample_rate (int): The sample rate of the audio (default 16000Hz for 16kHz audio).
    bit_depth (int): The bit depth of the audio (default 16 bits).
    channels (int): The number of audio channels (default 1 for mono audio).
    seconds (int): The number of seconds of audio to check for (default 20 seconds).

    Returns:
    bool: True if the buffer has at least `seconds` seconds of audio, False otherwise.
    """
    if byte_mode:
        required_bytes = bytes
        return buffer.tell() >= required_bytes
    
    if not byte_mode and bytes and bytes != 16000:
        raise ValueError("'bytes' argument is not applicable in non-byte mode")
    
    if byte_mode and seconds and seconds != 20:
        raise ValueError("'seconds' argument is not applicable in byte mode")
    
    if not buffer:
        return False
    
    bytes_per_sample = bit_depth // 8
    bytes_per_second = sample_rate * bytes_per_sample * channels
    required_seconds_bytes = seconds * bytes_per_second

    return buffer.tell() >= required_seconds_bytes
