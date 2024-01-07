# 「巡回セールスマン問題に対するQAOA: $W$状態を用いた初期状態の改良とNISQ時代の挑戦」における実験リポジトリ
このリポジトリの説明.

## 実行環境のセットアップ
実験の環境を作る.

### ローカル環境のセットアップ
`pip`を使用する場合, リポジトリのターミナル上で以下のコマンドを実行する.

```
pip install --upgrade pip
pip install -r requirements.txt
```
### IBM Quantum Platformのアカウントの作成

[ホームページ](https://quantum.ibm.com/)より指示に従ってアカウントを作る.

## 各フォルダの詳細
フォルダごとの説明.

### config
実験におけるパラメータの管理をするJSONファイルのフォルダ.

- job_conf.json
    - 
- meta.json
    - 実験時のパラメータを設定
        - "token": 「`******`」を自身のIBM Quantum PlatformのAPI Tokenに置き換える(<span style="color: red; ">必須</span>)
        - "shots": 量子回路のshotsを指定する
        - "iterations": 量子回路のパラメータ更新の回数を指定する
        - "reps": Hamiltonianの時間発展の回数を指定する
        - "problem": 問題を指定する
            - "data_path": 扱う問題のパスを指定する
            - "num_cities": 扱う問題の都市数を指定する
        - "optimizer": 古典最適化器の種類を選択する
            - {"cobyla", "nelder-mead", "powell", "spsa"}
        - "mode": 実験方法を選択する
            - {"device", "simulation"}
        - "quantum_machine": "mode"が"device"のとき, 「`------`」を使用するマシンの名前に置き換える(<span style="color: red; ">必須</span>)

### data
実験における問題を管理するTextファイルのフォルダ.

- tsp_data.txt
    - 基準となる5都市のTSP
    - AOJの[DPL_2_A](https://judge.u-aizu.ac.jp/onlinejudge/description.jsp?id=DPL_2_A)の21番目のデータ
- tsp_data_3_cities.txt
    - `tsp_data.txt`より作成した3都市のTSP
    - 都市数が変わってもプログラムが正常に動くかの確認用

### script
実験における実行プログラムを管理するPythonファイルのフォルダ.

- job_conv.py
    - 
- main.py
    - 
- utility_functions.py
    - 