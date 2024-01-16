import wave
import subprocess

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


def bytes_to_wav(byte_data, output_file, sample_rate=16000, num_channels=1, bit_depth=16):
    """
    Converts a bytes object to a .wav file.
    
    :param byte_data: Bytes object containing the audio data.
    :param output_file: Path to the output .wav file.
    :param sample_rate: Sample rate of the audio (default 44100 Hz).
    :param num_channels: Number of audio channels (default 1).
    :param bit_depth: Bit depth of the audio (default 16 bits).
    """
    try:
        # Ensure the byte_data length is divisible by sample width
        sample_width = bit_depth // 8
        remainder = len(byte_data) % sample_width
        if remainder != 0:
            # Append zeros to make it divisible
            byte_data += b'\x00' * (sample_width - remainder)

        with wave.open(output_file, 'wb') as wav_file:
            wav_file.setnchannels(num_channels)
            wav_file.setsampwidth(sample_width)
            wav_file.setframerate(sample_rate)
            wav_file.setnframes(len(byte_data) // sample_width)
            wav_file.writeframes(byte_data)

    except Exception as e:
        print(f"An error occurred: {e}")


def resample_audio(input_path, output_path, sample_rate=16000):
    try:
        subprocess.run(['ffmpeg', '-i', input_path, '-ar', str(sample_rate), output_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")