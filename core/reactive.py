import os
import glob
import subprocess
from pathlib import Path

# プロジェクトのルートディレクトリを特定
BASE_DIR = Path(__file__).resolve().parent.parent

def run_reactive_plugins(target_id=None):
    """
    プラグインを実行します。将来的にtarget_idを受け取ることで、
    特定のメッセージのみをプレビュー処理する拡張性を持たせています。
    """
    plugin_pattern = str(BASE_DIR / "plugin" / "reactive" / "[0-9]*.py")
    plugin_files = sorted(glob.glob(plugin_pattern))
    
    if not plugin_files:
        print("実行可能なリアクティブ・プラグインが見つかりません。")
        return

    for plugin in plugin_files:
        print(f"--- プラグイン実行開始: {os.path.basename(plugin)} ---", flush=True)
        try:
            # 環境変数を通じて、プラグインにターゲットIDを伝えることも可能です
            env = os.environ.copy()
            if target_id:
                env["POM_TARGET_UIDL"] = target_id
            
            subprocess.run(["python", plugin], check=True, cwd=str(BASE_DIR), env=env)
        except subprocess.CalledProcessError as e:
            print(f"プラグインの実行に失敗しました ({os.path.basename(plugin)}): {e}", flush=True)
        except Exception as e:
            print(f"予期せぬエラーが発生しました: {e}", flush=True)

if __name__ == "__main__":
    # 直接実行された場合は、全データへの再処理やデバッグとして機能
    print("【手動実行モード】リアクティブ・プロセスを開始します。")
    run_reactive_plugins()