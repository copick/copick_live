from setuptools import setup, find_packages

setup(
    name="copick_live",
    version="0.1.0",
    description="A live CoPick application",
    author="Zhuowen Zhao",
    author_email="kevin.zhao@czii.org",
    url="https://github.com/zhuowenzhao/copick_live",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "dash==2.13.0",
        "plotly==5.17.0",
        "pandas",
        "dash-extensions==1.0.1",
        "dash-bootstrap-components==1.5.0",
        "dash-iconify==0.1.2",
        "Flask==2.2.5",
        "numpy",
        "apscheduler",
        "pillow",
    ],
    dependency_links=[
        "git+https://github.com/uermel/copick.git#egg=copick"
    ],
    package_data={
        '': ['assets/*'],
    },
)
