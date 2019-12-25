
### Some details of content processing


`InputDirectory > Input > CxxProcessor > Combiner > GfmExporter`

#### CXX Processing Stage

* Strip whitespace (justified to first comment) and end of comment
* In statements all preceding whitespace is preserved
* Newlines converted into agnostic token ('newline')

e.g.

    // First line
    // Second line
    struct A {
      int b;
    };

Transformed into `Atom` objects with content:

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

* Combines contiguous comment and statements
* Multiple newlines in comments coalesced into double newline (content break)
* Emits chunks

`Chunk` have all the content stripped, combined and broken out into separate lists. A source file will emit multiple chunks for each viable chunk of content.

#### GfmExporter Stage

* Takes chunks and project settings
* Writes files in GFM format