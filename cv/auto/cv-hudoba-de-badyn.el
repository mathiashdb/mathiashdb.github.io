(TeX-add-style-hook
 "cv-hudoba-de-badyn"
 (lambda ()
   (TeX-add-to-alist 'LaTeX-provided-class-options
                     '(("article" "11pt" "letterpaper")))
   (TeX-add-to-alist 'LaTeX-provided-package-options
                     '(("biblatex" "sorting=none" "defernumbers=true" "backend=biber" "style=ieee" "datamodel=student" "maxcitenames=50" "maxnames=50") ("inputenc" "utf8") ("babel" "turkish" "english") ("geometry" "left=1in" "right=1in" "top=1in" "bottom=1in") ("xcolor" "usenames" "dvipsnames") ("hyperref" "colorlinks=true")))
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "href")
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "hyperimage")
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "hyperbaseurl")
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "nolinkurl")
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "url")
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "path")
   (add-to-list 'LaTeX-verbatim-macros-with-delims-local "path")
   (TeX-run-style-hooks
    "latex2e"
    "ref-format"
    "education"
    "interests"
    "grants_table"
    "publications"
    "awards"
    "talks"
    "press"
    "employment"
    "activities"
    "skills"
    "referees"
    "article"
    "art11"
    "ifthen"
    "longtable"
    "booktabs"
    "lscape"
    "floatrow"
    "biblatex"
    "inputenc"
    "fontspec"
    "babel"
    "anyfontsize"
    "datetime"
    "geometry"
    "enumitem"
    "xcolor"
    "fancyhdr"
    "framed"
    "hyperref"
    "etaremune")
   (TeX-add-symbols
    '("makefield" 2)
    '("resheading" 1)
    '("DOI" 1)
    "Title"
    "FirstName"
    "LastName"
    "Initials"
    "MyName"
    "MyRole"
    "Tian"
    "Email"
    "Website"
    "PhoneUS"
    "PhoneEU"
    "Affiliation"
    "Address"
    "invited"
    "cedilla"
    "turki")
   (LaTeX-add-bibliographies
    "1-journal-papers"
    "2-conference-papers"
    "3-nonpeer-conf"
    "4-inprep"
    "5-under-review"
    "6-theses"
    "7-talks"
    "8-press"
    "9-mentor"
    "10-abstracts"
    "11-phd")
   (LaTeX-add-counters
    "inPrepFlag")
   (LaTeX-add-lengths
    "outerbordwidth")
   (LaTeX-add-floatrow-DeclareNewOptions
    '("\\DeclareFloatFont{small}" "FloatFont" "small"))
   (LaTeX-add-xcolor-definecolors
    "shadecolor"
    "shadecolorB"
    "MarkerColour"))
 :latex)

