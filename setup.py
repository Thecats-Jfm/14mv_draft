from setuptools import setup, find_packages

setup(
    name="14mv_draft",
    version="0.5",
    packages=find_packages(),
    install_requires=[
        'PyQt5==5.12',
    ],
    entry_points={
        'console_scripts': [
            '14mvd=mv_draft.__main__:main', # 假设main函数在your_package/main.py中
        ],
    },
)
