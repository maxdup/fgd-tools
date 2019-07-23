def FgdWrite(fgd, filename):
    f = open(filename, "w")
    f.write(fgd.fgd_str())
