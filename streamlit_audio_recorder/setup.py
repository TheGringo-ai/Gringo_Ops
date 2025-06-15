from pathlib import Path
import setuptools

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setuptools.setup(
    name="streamlit-audiorec",
    version="0.1.3",
    author="Stefan Rummer",
    author_email="",
    description="Record audio from the user's microphone in apps that are deployed to the web. (via Browser Media-API) [GitHub ☆ 160+: steamlit-audio-recorder]",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/stefanrmmr/streamlit-audio-recorder",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    license="MIT",
    entry_points={
        "console_scripts": [
            "streamlit-audiorec=streamlit_audio_recorder:main",  # replace `main` with actual CLI if available
        ],
    },
    project_urls={
        "Bug Tracker": "https://github.com/stefanrmmr/streamlit-audio-recorder/issues",
        "Documentation": "https://github.com/stefanrmmr/streamlit-audio-recorder#readme",
        "Source Code": "https://github.com/stefanrmmr/streamlit-audio-recorder",
    },
    python_requires=">=3.7",
    install_requires=[
        "streamlit>=0.63",
    ],
)