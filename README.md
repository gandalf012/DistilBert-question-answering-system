# QA_DEMO: Web Interface for Question Answering System

A Question Answering Interface, based on the cdQA library.

## Installation

### From source 
```
git clone git@bitbucket.org:iobotguys/svc-qa-demo.git  
cd qa_demo

pip install -r requirements.txt
```

### Interface Lauching

```python
streamlit run qa_interface.py
```

### Docker
```
docker build -t "svc-qa-demo" .
./rundocker
```

### Manual

To use this infterface, you need to:

1. Select one database on the sidebar

2. Choose an article / put your own paragraph

3. Ask a question about this content. The answer to your question must be absolutely contained in the paragraph 

4. Press the button **Predict answers** to obtain your answer
