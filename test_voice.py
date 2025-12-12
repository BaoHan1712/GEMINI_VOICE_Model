import asyncio
import wave
import traceback
from google import genai
from google.genai.types import LiveConnectConfig, PrebuiltVoiceConfig

# --- CẤU HÌNH ---
# Lưu ý: Tôi đã ẩn API Key của bạn để bảo mật. Hãy điền lại vào đây.
API_KEY = "API_KEY_CỦA_BẠN" 
OUTPUT_FILE = "gemini_voice.wav"

# KHUYẾN NGHỊ: Hãy dùng "gemini-2.0-flash-exp" nếu cái 2.5 bên dưới báo lỗi
MODEL_ID = "gemini-2.5-flash-native-audio-latest" 
# MODEL_ID = "gemini-2.5-flash-native-audio-latest" 

async def main():
    client = genai.Client(api_key=API_KEY)
    
    config = LiveConnectConfig(
        response_modalities=["AUDIO"], # Chỉ lấy Audio về
        speech_config=genai.types.SpeechConfig(
            voice_config=PrebuiltVoiceConfig(
                voice_name="Puck" # Các giọng khác: Charon, Kore, Fenrir, Aoede
            )
        )
    )

    print(f"--- Đang kết nối tới model: {MODEL_ID} ---")
    
    try:
        async with client.aio.live.connect(model=MODEL_ID, config=config) as session:
            
            # --- PHẦN THAY ĐỔI: NHẬP TỪ BÀN PHÍM ---
            print("\n" + "="*40)
            user_input = input("👉 Nhập câu hỏi của bạn: ")
            print("="*40 + "\n")
            
            print(f"Đang gửi lên server: \"{user_input}\"...")
            
            # Gửi text lên
            await session.send(input=user_input, end_of_turn=True)

            # Nhận audio về
            with wave.open(OUTPUT_FILE, 'wb') as wav_file:
                # Cấu hình file wav chuẩn của Gemini (24kHz, 1 kênh, 16bit)
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(24000)
                
                print("🔊 Đang nhận câu trả lời (ghi vào file)...")
                
                async for response in session.receive():
                    # Ghi dữ liệu âm thanh vào file
                    if response.data:
                        wav_file.writeframes(response.data)
                        print(".", end="", flush=True) # Hiệu ứng loading
                    
                    # Kiểm tra xem AI đã nói xong chưa
                    if response.server_content and response.server_content.turn_complete:
                        print("\n✅ Đã nhận xong câu trả lời.")
                        break
                        
        print(f"\n🎉 Thành công! Mở file '{OUTPUT_FILE}' để nghe câu trả lời.")

    except Exception as e:
        print("\n❌ LỖI XẢY RA:")
        # In chi tiết lỗi để dễ debug
        traceback.print_exc() 
        
        err_str = str(e)
        if "404" in err_str or "not found" in err_str or "1008" in err_str:
            print(f"\n>>> CẢNH BÁO: Tên model '{MODEL_ID}' không đúng hoặc không hỗ trợ Live API.")
            print(">>> Hãy đổi lại MODEL_ID = 'gemini-2.0-flash-exp' ở đầu file code.")

if __name__ == "__main__":
    asyncio.run(main())