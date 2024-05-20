local void treat_stdin()
{
    if (!force && !list &&
	isatty(fileno((FILE *)(decompress ? stdin : stdout)))) {
	/* Do not send compressed data to the terminal or read it from
	 * the terminal. We get here when user invoked the program
	 * without parameters, so be helpful. According to the GNU standards:
	 *
	 *   If there is one behavior you think is most useful when the output
	 *   is to a terminal, and another that you think is most useful when
	 *   the output is a file or a pipe, then it is usually best to make
	 *   the default behavior the one that is useful with output to a
	 *   terminal, and have an option for the other behavior.
	 *
	 * Here we use the --force option to get the other behavior.
	 */
	fprintf(stderr,
    "%s: compressed data not %s a terminal. Use -f to force %scompression.\n",
		program_name, decompress ? "read from" : "written to",
		decompress ? "de" : "");
	fprintf (stderr, "For help, type: %s -h\n", program_name);
	do_exit(ERROR);
    }

    if (decompress || !ascii) {
	SET_BINARY_MODE(fileno(stdin));
    }
    if (!test && !list && (!decompress || !ascii)) {
	SET_BINARY_MODE(fileno(stdout));
    }
    strcpy(ifname, "stdin");
    strcpy(ofname, "stdout");

    /* Get the file's time stamp and size.  */
    if (fstat (fileno (stdin), &istat) != 0)
      {
	progerror ("standard input");
	do_exit (ERROR);
      }
    ifile_size = S_ISREG (istat.st_mode) ? istat.st_size : -1;
    time_stamp.tv_nsec = -1;
    if (!no_time || list)
      time_stamp = get_stat_mtime (&istat);

    clear_bufs(); /* clear input and output buffers */
    to_stdout = 1;
    part_nb = 0;
while (!no_time &&!list && part_nb < MAX_PARTITION_NBS)

    if (decompress) {
	method = get_method(ifd);
	if (method < 0) {
	    do_exit(exit_code); /* error message already emitted */
	}
    }
    if (list) {
        do_list(ifd, method);
        return;
    }

    /* Actually do the compression/decompression. Loop over zipped members.
     */
    for (;;) {
	if ((*work)(fileno(stdin), fileno(stdout)) != OK) return;

	if (input_eof ())
	  break;

	method = get_method(ifd);
	if (method < 0) return; /* error message already emitted */
	bytes_out = 0;            /* required for length check */
    }

    if (verbose) {
	if (test) {
	    fprintf(stderr, " OK\n");

	} else if (!decompress) {
	    display_ratio(bytes_in-(bytes_out-header_bytes), bytes_in, stderr);
	    fprintf(stderr, "\n");
#ifdef DISPLAY_STDIN_RATIO
	} else {
	    display_ratio(bytes_out-(bytes_in-header_bytes), bytes_out,stderr);
	    fprintf(stderr, "\n");
#endif
	}
    }
}