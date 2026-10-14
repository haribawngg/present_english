"""Build a portable source ZIP and Colab notebook; excludes venv and caches."""
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def cell(kind, source):
    result = {"cell_type": kind, "metadata": {}, "source": source.splitlines(keepends=True)}
    if kind == "code":
        result.update(execution_count=None, outputs=[])
    return result


cells = [
    cell("markdown", "# Phân loại SMS: Naive Bayes, Logistic Regression và Dense Network\n"
         "Notebook chạy source trong gói đính kèm. Chọn Runtime → Run all cho phần cơ bản; "
         "neural bật riêng ở cell cuối. Spam là positive class; cùng split seed=42, test=20%."),
    cell("code", "from google.colab import files\nfrom pathlib import Path\nimport zipfile\n"
         "uploaded = files.upload()  # Chọn sms_spam_lab.zip\n"
         "archive = next(name for name in uploaded if name.endswith('.zip'))\n"
         "with zipfile.ZipFile(archive) as z:\n"
         "    root = Path('/content/sms_spam_lab').resolve()\n"
         "    for item in z.infolist():\n"
         "        if not (root / item.filename).resolve().is_relative_to(root):\n"
         "            raise ValueError('Unsafe ZIP path')\n"
         "    z.extractall(root)\n%cd /content/sms_spam_lab\n%pip install -q -r requirements.txt"),
    cell("markdown", "## 1–2. Pandas và chuẩn hóa NLTK\nLemmatization có POS rồi stemming; "
         "không fit bất kỳ thống kê nào trên test. Đọc thêm giải thích chi tiết trong README.md."),
    cell("code", "from spam_lab.preprocessing import setup_resources, Normalizer\n"
         "from spam_lab.train import load_data\nsetup_resources()\n"
         "df, total = load_data('data/smsspamcollection.tsv')\ndisplay(df.head())\n"
         "display(df.label.value_counts())\nprint(Normalizer()('Cats were running. Call 123 now!'))"),
    cell("markdown", "## 3–8. Train/test, vocabulary train, NB bằng Counter và hai baseline LR\n"
         "Dùng thư mục có thời gian để có thể chạy lại cell mà không ghi đè kết quả trước."),
    cell("code", "from datetime import datetime\nfrom spam_lab.train import train\n"
         "output = 'colab_artifacts_' + datetime.now().strftime('%Y%m%d_%H%M%S_%f')\n"
         "report = train('data/smsspamcollection.tsv', output=output)\nreport['metadata']"),
    cell("code", "import pandas as pd\nfrom IPython.display import Image, display\n"
         "display(pd.read_csv(f'{output}/comparison.csv'))\n"
         "display(Image(filename=f'{output}/confusion_matrices.png'))\n"
         "display(pd.read_csv(f'{output}/nb_vocabulary.csv').head(20))"),
    cell("markdown", "Confusion matrix: hàng là nhãn thật, cột là dự đoán, thứ tự ham/spam. "
         "Accuracy=(TP+TN)/N; precision=TP/(TP+FP); recall=TP/(TP+FN). "
         "So sánh F1 và recall bên cạnh accuracy vì mất cân bằng lớp."),
    cell("code", "from spam_lab.inference import Predictor\npredictor = Predictor(output)\n"
         "predictor.predict(['You won free cash! Call now', 'See you tonight'], explain=True)"),
    cell("markdown", "## 9*. Dense Network tùy chọn\nĐổi RUN_NEURAL=True. "
         "Validation tách từ train, không dùng test để EarlyStopping."),
    cell("code", "RUN_NEURAL = False\nif RUN_NEURAL:\n"
         "    import subprocess, sys\n"
         "    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements-neural.txt'])\n"
         "    neural_output = output + '_neural'\n"
         "    neural_report = train('data/smsspamcollection.tsv', output=neural_output, neural=True)\n"
         "    display(pd.read_csv(f'{neural_output}/comparison.csv'))"),
    cell("code", "import shutil\nshutil.make_archive(output, 'zip', output)\nfiles.download(output + '.zip')"),
    cell("markdown", "## Nộp bài và demo\nLưu notebook vào Drive rồi Share để lấy link Colab. "
         "Dùng kết quả chạy thực tế và confusion matrix để viết báo cáo PDF. "
         "Backend local: `python run_demo.py`; "
         "hướng dẫn API và frontend fetch có trong README.md."),
]
notebook = {"cells": cells, "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                                            "language_info": {"name": "python"}, "colab": {"name": "sms_spam_lab.ipynb"}},
            "nbformat": 4, "nbformat_minor": 4}
(ROOT / "notebooks").mkdir(exist_ok=True)
(ROOT / "notebooks/sms_spam_lab.ipynb").write_text(json.dumps(notebook, indent=2, ensure_ascii=False), encoding="utf-8")
with zipfile.ZipFile(ROOT / "sms_spam_lab.zip", "w", zipfile.ZIP_DEFLATED) as archive:
    for folder in ["spam_lab", "backend", "frontend", "scripts", "tests", "tools", "notebooks", "data", "artifacts", "artifacts_neural_verified"]:
        for path in (ROOT / folder).rglob("*"):
            if path.is_file() and "__pycache__" not in path.parts and "node_modules" not in path.parts:
                archive.write(path, path.relative_to(ROOT))
    for name in ["package.json", "package-lock.json", "README.md", "DEMO.md", "ARCHITECTURE.md", "SETUP_LAPTOP.md", "run_demo.py", "start_demo.ps1", "requirements.txt", "requirements-dev.txt", "requirements-neural.txt", "requirements-tested.txt", "pytest.ini", ".gitignore"]:
        if (ROOT / name).exists():
            archive.write(ROOT / name, name)
print(ROOT / "sms_spam_lab.zip")
