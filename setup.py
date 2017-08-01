from setuptools import setup, find_packages

setup(name='dosido',
      version='1.0',
      description='Manage HelpScout knowledge base with VCS markdown',
      url='https://github.com/TannerBaldus/dosido',
      author='Tanner Baldus',
      author_email='me@tannerbaldus.com',
      license='MIT',
      install_requires=[
            "beautifulsoup4==4.6.0",
            "certifi==2017.4.17",
            "chardet==3.0.4",
            "docopt==0.6.2",
            "idna==2.5",
            "Markdown==2.6.8",
            "requests==2.18.2",
            "urllib3==1.22",
      ],
      keywords='helpscout markdown docs documentation github vcs knowledge base',
      packages=find_packages(),
      entry_points={
            'console_scripts': ['dosido = dosido.main:main'],
      },
      zip_safe=False)