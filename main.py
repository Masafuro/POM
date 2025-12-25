import os
import time
import subprocess
import glob
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from core.intake import intake

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

def run_reactive_plugins():
    plugin_pattern = str(BASE_DIR / "reactive" / "[0-9]*.py")
    plugin_files = sorted(glob.glob(plugin_pattern))
    for plugin in plugin_files:
        print(f"--- プラグイン実行: {plugin} ---", flush=True)
        try:
            subprocess.run(["python", plugin], check=True, cwd=str(BASE_DIR))
        except Exception as e:
            print(f"エラー発生 ({plugin}): {e}", flush=True)

def main():
    polling_raw = os.getenv("POLLING_INTERVAL", "600")
    # 数値以外の文字列を無視して整数に変換します
    interval = int(''.join(filter(str.isdigit, polling_raw)))
    
    print("==================================================", flush=True)
    print(" POM サービスが開始されました", flush=True)
    print(f" 実行間隔: {interval}秒", flush=True)
    print("==================================================", flush=True)

    while True:
        try:
            print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] サイクル開始", flush=True)
            intake()
            run_reactive_plugins()
            print(f"サイクル完了。次回の実行まで {interval}秒 待機します。", flush=True)
        except Exception as e:
            print(f"メインループでエラーが発生しました: {e}", flush=True)
        time.sleep(interval)

if __name__ == "__main__":
    main()