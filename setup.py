from setuptools import setup, find_packages
with open('requirements.txt') as f:
    required = f.read().splitlines()
setup(
    name="14mv_draft",
    version="0.5",
    packages=find_packages(),
    install_requires=required,
    entry_points={
        'console_scripts': [
            '14mvd=mv_draft.__main__:main', # 假设main函数在your_package/main.py中
        ],
    },
)
