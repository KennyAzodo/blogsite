$(document).ready(function () {
  $('.menu-toggle').on('Click', function () {
    $('.nav').toggleClass('.showing')
    $('.nav ul').toggleClass('.showing')
  })

  $('.post-wrapper').slick({
    slidesToShow: 3,
    slidesToScroll: 1,
    autoplay: true,
    autoplaySpeed: 2000,
    nextArrow: $('.next'),
    prevArrow: $('.prev'),
  })
  responsive: [
    {
      breakpoint: 1024,
      settings: {
        slidesToShow: 3,
        slidesToScroll: 3,
        infinite: true,
        dots: true,
      },
    },
    {
      breakpoint: 600,
      settings: {
        slidesToShow: 2,
        slidesToScroll: 2,
      },
    },
    {
      breakpoint: 480,
      settings: {
        slidesToShow: 1,
        slidesToScroll: 1,
      },
    },
    // You can unslick at a given breakpoint now by adding:
    // settings: "unslick"
    // instead of a settings object
  ]
})

// const { ClassicEditor, Essentials, Bold, Italic, Font, Paragraph } = CKEDITOR

// ClassicEditor.create(document.querySelector('#body'), {
//   licenseKey: '<YOUR_LICENSE_KEY>',
//   plugins: [Essentials, Bold, Italic, Font, Paragraph],
//   toolbar: [
//     'undo',
//     'redo',
//     '|',
//     'bold',
//     'italic',
//     '|',
//     'fontSize',
//     'fontFamily',
//     'fontColor',
//     'fontBackgroundColor',
//   ],
// })
//   .then(/* ... */)
//   .catch(/* ... */)

const {
  ClassicEditor,
  Alignment,
  Autoformat,
  AutoImage,
  AutoLink,
  Autosave,
  BlockQuote,
  Bold,
  Bookmark,
  CloudServices,
  Code,
  CodeBlock,
  Essentials,
  FontBackgroundColor,
  FontColor,
  FontFamily,
  FontSize,
  GeneralHtmlSupport,
  Heading,
  Highlight,
  HorizontalLine,
  ImageBlock,
  ImageCaption,
  ImageInline,
  ImageInsertViaUrl,
  ImageResize,
  ImageStyle,
  ImageTextAlternative,
  ImageToolbar,
  ImageUpload,
  Indent,
  IndentBlock,
  Italic,
  Link,
  List,
  ListProperties,
  MediaEmbed,
  Paragraph,
  PasteFromOffice,
  RemoveFormat,
  Strikethrough,
  Style,
  Subscript,
  Superscript,
  Table,
  TableCaption,
  TableCellProperties,
  TableColumnResize,
  TableProperties,
  TableToolbar,
  TextPartLanguage,
  TextTransformation,
  Title,
  TodoList,
  Underline,
} = window.CKEDITOR

const LICENSE_KEY =
  'eyJhbGciOiJFUzI1NiJ9.eyJleHAiOjE3MzU0MzAzOTksImp0aSI6ImY1YjE3YWVkLTcwMWMtNDhiMS1hYjBiLTA4ZWZlOWNlZGNlYSIsInVzYWdlRW5kcG9pbnQiOiJodHRwczovL3Byb3h5LWV2ZW50LmNrZWRpdG9yLmNvbSIsImRpc3RyaWJ1dGlvbkNoYW5uZWwiOlsiY2xvdWQiLCJkcnVwYWwiLCJzaCJdLCJ3aGl0ZUxhYmVsIjp0cnVlLCJsaWNlbnNlVHlwZSI6InRyaWFsIiwiZmVhdHVyZXMiOlsiKiJdLCJ2YyI6IjRhZTYyOTU0In0.9-7ljbm319sQc_GWxsn7X4jUGqsTjlWCkh5Pgy_gutFN_YiLhPAMFqN7bhwVcWvTgtkoQhhLZOZ9CMyyZ1Vk_A'

const editorConfig = {
  toolbar: {
    items: [
      'textPartLanguage',
      '|',
      'heading',
      'style',
      '|',
      'fontSize',
      'fontFamily',
      'fontColor',
      'fontBackgroundColor',
      '|',
      'bold',
      'italic',
      'underline',
      'strikethrough',
      'subscript',
      'superscript',
      'code',
      'removeFormat',
      '|',
      'horizontalLine',
      'link',
      'bookmark',
      'mediaEmbed',
      'insertTable',
      'highlight',
      'blockQuote',
      'codeBlock',
      '|',
      'alignment',
      '|',
      'bulletedList',
      'numberedList',
      'todoList',
      'outdent',
      'indent',
    ],
    shouldNotGroupWhenFull: false,
  },
  plugins: [
    Alignment,
    Autoformat,
    AutoImage,
    AutoLink,
    Autosave,
    BlockQuote,
    Bold,
    Bookmark,
    CloudServices,
    Code,
    CodeBlock,
    Essentials,
    FontBackgroundColor,
    FontColor,
    FontFamily,
    FontSize,
    GeneralHtmlSupport,
    Heading,
    Highlight,
    HorizontalLine,
    ImageBlock,
    ImageCaption,
    ImageInline,
    ImageInsertViaUrl,
    ImageResize,
    ImageStyle,
    ImageTextAlternative,
    ImageToolbar,
    ImageUpload,
    Indent,
    IndentBlock,
    Italic,
    Link,
    List,
    ListProperties,
    MediaEmbed,
    Paragraph,
    PasteFromOffice,
    RemoveFormat,
    Strikethrough,
    Style,
    Subscript,
    Superscript,
    Table,
    TableCaption,
    TableCellProperties,
    TableColumnResize,
    TableProperties,
    TableToolbar,
    TextPartLanguage,
    TextTransformation,
    Title,
    TodoList,
    Underline,
  ],
  fontFamily: {
    supportAllValues: true,
  },
  fontSize: {
    options: [10, 12, 14, 'default', 18, 20, 22],
    supportAllValues: true,
  },
  heading: {
    options: [
      {
        model: 'paragraph',
        title: 'Paragraph',
        class: 'ck-heading_paragraph',
      },
      {
        model: 'heading1',
        view: 'h1',
        title: 'Heading 1',
        class: 'ck-heading_heading1',
      },
      {
        model: 'heading2',
        view: 'h2',
        title: 'Heading 2',
        class: 'ck-heading_heading2',
      },
      {
        model: 'heading3',
        view: 'h3',
        title: 'Heading 3',
        class: 'ck-heading_heading3',
      },
      {
        model: 'heading4',
        view: 'h4',
        title: 'Heading 4',
        class: 'ck-heading_heading4',
      },
      {
        model: 'heading5',
        view: 'h5',
        title: 'Heading 5',
        class: 'ck-heading_heading5',
      },
      {
        model: 'heading6',
        view: 'h6',
        title: 'Heading 6',
        class: 'ck-heading_heading6',
      },
    ],
  },
  htmlSupport: {
    allow: [
      {
        name: /^.*$/,
        styles: true,
        attributes: true,
        classes: true,
      },
    ],
  },
  image: {
    toolbar: [
      'toggleImageCaption',
      'imageTextAlternative',
      '|',
      'imageStyle:inline',
      'imageStyle:wrapText',
      'imageStyle:breakText',
      '|',
      'resizeImage',
    ],
  },
  initialData: ' ',
  licenseKey: LICENSE_KEY,
  link: {
    addTargetToExternalLinks: true,
    defaultProtocol: 'https://',
    decorators: {
      toggleDownloadable: {
        mode: 'manual',
        label: 'Downloadable',
        attributes: {
          download: 'file',
        },
      },
    },
  },
  list: {
    properties: {
      styles: true,
      startIndex: true,
      reversed: true,
    },
  },
  placeholder: 'Type or paste your content here!',
  style: {
    definitions: [
      {
        name: 'Article category',
        element: 'h3',
        classes: ['category'],
      },
      {
        name: 'Title',
        element: 'h2',
        classes: ['document-title'],
      },
      {
        name: 'Subtitle',
        element: 'h3',
        classes: ['document-subtitle'],
      },
      {
        name: 'Info box',
        element: 'p',
        classes: ['info-box'],
      },
      {
        name: 'Side quote',
        element: 'blockquote',
        classes: ['side-quote'],
      },
      {
        name: 'Marker',
        element: 'span',
        classes: ['marker'],
      },
      {
        name: 'Spoiler',
        element: 'span',
        classes: ['spoiler'],
      },
      {
        name: 'Code (dark)',
        element: 'pre',
        classes: ['fancy-code', 'fancy-code-dark'],
      },
      {
        name: 'Code (bright)',
        element: 'pre',
        classes: ['fancy-code', 'fancy-code-bright'],
      },
    ],
  },
  table: {
    contentToolbar: [
      'tableColumn',
      'tableRow',
      'mergeTableCells',
      'tableProperties',
      'tableCellProperties',
    ],
  },
}

ClassicEditor.create(document.querySelector('#editor'), editorConfig)
