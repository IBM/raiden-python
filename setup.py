from setuptools import setup

setup(
    name='raiden-python',
    version='1.0.0',    
    description='Raiden api',
    url='',
    author='Grzegorz Wypych (h0rac) & Adam Laurie (M@jor Malfunction)',
    author_email='',
    license='BSD 3-clause',
    packages=['raiden-python'],
    install_requires=['pySerial',                  
                      ],

   classifiers=[
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',  
        'Programming Language :: Python :: 3',

    ],                   
)