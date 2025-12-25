import os
import time
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from core.intake import intake
from core.reactive import run_reactive_plugins

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

def main():
    polling_raw = os.getenv("POLLING_INTERVAL", "600")
    # 数値以外の文字列を無視して整数に変換
    interval = int(''.join(filter(str.isdigit, polling_raw)))
    
    print("==================================================", flush=True)
    print(" POM サービスが正常に起動しました", flush=True)
    print(f" 稼働環境: {BASE_DIR}")
    print(f" 監視間隔: {interval}秒")
    print("==================================================", flush=True)

    while True:
        try:
            now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"\n[{now_str}] サイクルを開始します。", flush=True)
            
            # ステージ1: インテイク（データの取り込み）
            print(">> ステージ1: インテイク実行中...", flush=True)
            intake()
            
            # ステージ2: リアクティブ（データの加工・反応）
            print(">> ステージ2: リアクティブ・プラグイン実行中...", flush=True)
            run_reactive_plugins()
            
            print(f"[{now_str}] サイクルが正常に完了しました。", flush=True)
            print(f"次回の実行まで {interval}秒 待機します。", flush=True)
            
        except Exception as e:
            print(f"【致命的なエラー】メインループ内で問題が発生しました: {e}", flush=True)
        
        time.sleep(interval)

if __name__ == "__main__":
    main()