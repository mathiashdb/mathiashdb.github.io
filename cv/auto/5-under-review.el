(TeX-add-style-hook
 "5-under-review"
 (lambda ()
   (LaTeX-add-bibitems
    "nik_vpp_ifac"
    "marioicon"
    "seb_gs_ifac"
    "seb_auv_cep"
    "selftuning_journal"))
 '(or :bibtex :latex))

