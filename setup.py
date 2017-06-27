try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(
    name='txstripe',
    version='0.1.0',
    description='Stripe Twisted bindings',
    author='Lex Toumbourou',
    author_email='lextoumbourou@gmail.com',
    url='https://github.com/lextoumbourou/txstripe',
    packages=['stripe', 'txstripe'],
    install_requires=['Twisted', 'treq'],
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ]
)
