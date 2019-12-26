# Make C/C++ documentation simple

`cxmeta` is a tool for making it simple to create good looking documentation directly from your C/C++ source code.

While there are ways to make more attractive or feature-rich documentation, the tools are complicated and create extra work.

The hope for this tool is that it can find a good mix of simplicity and flexibility so that writing good documentation for your project is a no-brainer.

## Run It!

    pip install cxmeta
    cxmeta <directory or file>

`cxmeta` is an opinionated and simple-minded tool, it wants to generate a README.md in your local directory.

`cxmeta` prefers GitHub flavored markdown which you can easily preview using `grip`:

    pip install grip
    grip

:electric_plug: Have a *README.md* or structure in mind? You can modifying the behavior of `cxmeta` through [configuration](DETAILS.md).

:triangular_ruler: If you want to style your documents or put out a different format Modifying the style of cxmeta requires [templates](DETAILS.md).


:chart_with_upwards_trend: [Interested in more? Read and profit!](DETAILS.md)

:gift: [Want to contribute? Small gifts are welcome](CONTRIBUTING.md)

## Additional Reading

* [Mastering Markdown](https://guides.github.com/features/mastering-markdown/)
* [Commonalities between rST and Markdown](https://gist.github.com/dupuy/1855764)
