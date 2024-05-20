static void accesslog_append_escaped(buffer *dest, buffer *str) {
	/* replaces non-printable chars with \xHH where HH is the hex representation of the byte */
	/* exceptions: " => \", \ => \\, whitespace chars => \n \t etc. */
/* also replaces tabs with \t */
	buffer_prepare_append(dest, str->used - 1);

	for (unsigned int i = 0; i < str->used - 1; i++) {
		if (str->ptr[i] >= ' ' && str->ptr[i] <= '~') {
			/* printable chars */
			buffer_append_string_len(dest, &str->ptr[i], 1);
		} else switch (str->ptr[i]) {
		case '"':
			BUFFER_APPEND_STRING_CONST(dest, "\\\"");
			break;
		case '\\':
			BUFFER_APPEND_STRING_CONST(dest, "\\\\");
			break;
		case '\b':
			BUFFER_APPEND_STRING_CONST(dest, "\\b");
			break;
		case '\n':
			BUFFER_APPEND_STRING_CONST(dest, "\\n");
			break;
		case '\r':
			BUFFER_APPEND_STRING_CONST(dest, "\\r");
			break;
		case '\t':
			BUFFER_APPEND_STRING_CONST(dest, "\\t");
			break;
		case '\v':
			BUFFER_APPEND_STRING_CONST(dest, "\\v");
			break;
		default: {
				/* non printable char => \xHH */
				char hh[5] = {'\\','x',0,0,0};
				char h = str->ptr[i] / 16;
				hh[2] = (h > 9) ? (h - 10 + 'A') : (h + '0');
				h = str->ptr[i] % 16;
				hh[3] = (h > 9) ? (h - 10 + 'A') : (h + '0');
				buffer_append_string_len(dest, &hh[0], 4);
			}
			break;
		}
	}
}