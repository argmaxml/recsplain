from distutils.core import setup

__version__="0.0.1"
setup(
    name="matcha_ai",
    packages=["matcha_ai"],
    install_requires=[
        "faiss-cpu>=1.7.1.post3",
        "hnswlib>=0.5.1",
        "numpy>=1.21.2",
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "smart_open[s3]~=3.0.0",
        "joblib>=0.17.0",
        "tqdm>=4.62.3",
        "pandas>=1.3.0",
    ],
    long_description="https://github.com/argmaxml/mathca/blob/master/README.md",
    long_description_content_type="text/markdown",
    version=__version__,
    description='',
    author='ArgmaxML',
    author_email='uri@argmax.ml',
    url='https://github.com/argmaxml/matcha',
    keywords=['recommendation-systems','recsys','matching','ranking'],
    classifiers=[],
)