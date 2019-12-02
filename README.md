# C eXtract Metadata

A python CLI and library to extract meta-data from Cxx style languages.

This is not intended to be a full AST style exploration for static analysis. 

Instead, the goal is to pull embedded metadata and accompanying declarations from the code in order to support tasks such as DRY documentation.

C source | meta-data | Markdown/rST documentation

I couldn't find any tools that made this process simple and effective. Initially I built a very small python script
that would pull very-specifically formatted headers into markdown. This process was heavily opinionated in it's formatting
requirements and brittle and inflexible in implementation. 

This new approach is to provide a more flexible and powerful processing pipeline for the code which exposes comments, 
statements and expressions into a stream which can extract metadata.

Additional meta-data rules at the end of the pipeline allow for rST authoring to make it simple for the source code author to export 
their types into simple and attractive documentation.

Common styles between rST and Markdown: https://gist.github.com/dupuy/1855764
