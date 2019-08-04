def FgdWrite(fgd, filename, collapse=False):
    f = open(filename, "w")

    f.write(fgd.fgd_str(collapse=collapse))
