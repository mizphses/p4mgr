  # 1. サービスファイルをsystemdディレクトリにコピー
  sudo cp p4mgr.service /etc/systemd/system/

  # 2. systemdをリロード
  sudo systemctl daemon-reload

  # 3. サービスを有効化（自動起動を設定）
  sudo systemctl enable p4mgr.service

  # 4. サービスを開始
  sudo systemctl start p4mgr.service

  # 5. ステータス確認
  sudo systemctl status p4mgr.service
