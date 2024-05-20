TIFFFetchData(TIFF* tif, TIFFDirEntry* dir, char* cp)
{
	int w = TIFFDataWidth((TIFFDataType) dir->tdir_type);
	tsize_t cc = dir->tdir_count * w;

	/* Check for overflow. */
if ((cc > 0x7fffffff) || (cc < -0x7fffffff)) {
		goto bad;

	if (!isMapped(tif)) {
		if (!SeekOK(tif, dir->tdir_offset))
			goto bad;
		if (!ReadOK(tif, cp, cc))
			goto bad;
	} else {
		tsize_t offset = dir->tdir_offset + cc;
		/* Check for overflow. */
		if ((tsize_t)dir->tdir_offset != offset - cc
		    || offset > (tsize_t)tif->tif_size)
			goto bad;
		_TIFFmemcpy(cp, tif->tif_base + dir->tdir_offset, cc);
	}
	if (tif->tif_flags & TIFF_SWAB) {
		switch (dir->tdir_type) {
		case TIFF_SHORT:
		case TIFF_SSHORT:
			TIFFSwabArrayOfShort((uint16*) cp, dir->tdir_count);
			break;
		case TIFF_LONG:
		case TIFF_SLONG:
		case TIFF_FLOAT:
			TIFFSwabArrayOfLong((uint32*) cp, dir->tdir_count);
			break;
		case TIFF_RATIONAL:
		case TIFF_SRATIONAL:
			TIFFSwabArrayOfLong((uint32*) cp, 2*dir->tdir_count);
			break;
		case TIFF_DOUBLE:
			TIFFSwabArrayOfDouble((double*) cp, dir->tdir_count);
			break;
		}
	}
	return (cc);
bad:
	TIFFErrorExt(tif->tif_clientdata, tif->tif_name,
		     "Error fetching data for field \"%s\"",
		     _TIFFFieldWithTag(tif, dir->tdir_tag)->field_name);
	return (tsize_t) 0;
}