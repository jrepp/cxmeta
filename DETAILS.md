# Details

This document is intended to help orient people who need to dig deeper to configure `cxmeta` or change the style of their documentation.


## Rationale

`cxmeta` does not intended to be a full AST style exploration for static analysis.

Instead, the goal is to pull embedded metadata and accompanying declarations from code to to write DRY documentation.

I think there are some powerful things that can be done at the level that `cxmeta` operates and after exploring the AST route for some time I decided to abandon it due to the inherit complexity.

Instead of an AST, an object pipeline is used to process source files into rendered documents. At the front of the pipeline are source files, converted into lines, tokenized by regular expressions and assembled into chunks of metadata.

The pipeline is intended to be fairly compos-able and configurable.

However, we should never ask anyone to compose a configurable pipeline to create documentation. I consider that a failure mode. It should be simple and straightforward to make good documentation and possible to craft impressive use-cases that resemble the core use case.

### Content processing

The default content processing pipeline looks like the following:

`InputDirectory > Input > CxxProcessor > Combiner > GfmExporter`

Each stage has input types and output types and is connected by streams.

## Working with structure

The default structure supported by `cxmeta` is a single project processing some files in a directory. The output of the project is a README.md.

The first thing you might want to do is to add an index or extra usage of `cxmeta` beyond generating a *README.md*

`cxmeta` works from a principal of whitelisting requiring all directories and files to be explicitily added rather than ignored or blacklisted.


### Use your own README.md

### Multiple files

### Nested directories

Additional meta-data rules at the end of the pipeline allow for rST authoring to make it simple for the source code author to export
their types into simple and attractive documentation.

#### CXX Processing Stage

This stage operates on lines, and it's goal is to separate out the arcane uterances of C/C++ code into digestable chunks for further stages.

Whitespace is a thing that must be properly dealt with. The general theory is to preserve the structural content of each line while trivially discard anything unneccessary for later stages.

* Strip comment whitespace, left justified and end of line
* Preserve preceding whitespace of code
* Convert newlines into markers
* Inject content verbatim into the stream with statement markers

e.g.

    // First line
    // Second line
    struct A {
      int b;
    };

Transforms into a stream of `cxmeta.pipeline.stream.Atom`:

    [
      {type: 'comment_start'},
      {type: 'content', value: 'First line'},
      {type: 'newline' },
      {type: 'comment_end'},
      {type: 'comment_start'},
      {type: 'content', value: 'Second line'}
      {type: 'newline'},
      {type: 'comment_end'},
      {type: 'content', value: 'struct A'}
      {type: 'block_start'}
      {type: 'content', is_comment: False, content: '  int b;'}
      {type: 'stmt_end'}
      {type: 'content', value: '};'}
      {type: 'block_end'}
    ]


#### Combiner Stage

`cxmeta.pipeline.stream.Chunk` objects have all the content stripped, combined and broken out into separate lists. A source file will emit multiple chunks for each viable chunk of content.

* Combines contiguous comment and statements
* Coalesced multiple newlines into double newline (a content break)
* Emits chunks


#### GfmExporter Stage

* Takes chunks and project settings
* Writes files in GFM format


### Background

I couldn't find any tools that made this process simple and effective. Initially I built a very small python script
that would pull very-specifically formatted headers into markdown. This process was heavily opinionated in it's formatting
requirements and brittle and inflexible in implementation.

To support additional projects some more flexible and a processing pipeline for the code which exposes comments,
statements, expressions and metadata into a stream seemed like a better choice.