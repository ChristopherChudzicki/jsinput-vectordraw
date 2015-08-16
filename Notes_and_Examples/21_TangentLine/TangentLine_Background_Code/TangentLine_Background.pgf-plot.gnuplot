set table "TangentLine_Background.pgf-plot.table"; set format "%.5f"
set format "%.7e";; set contour base; set cntrparam levels discrete 0.0; unset surface; set view map; set isosamples 500; splot y**4+x*y-x**3+x-2; 
