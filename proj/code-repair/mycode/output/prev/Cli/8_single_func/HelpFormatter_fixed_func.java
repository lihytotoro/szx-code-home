    while (true)
    {
        text = padding + text.substring(pos).trim();
        pos = findWrapPos(text, width, nextLineTabStop);
    
        if (pos == -1)
        {
            sb.append(text);
    
            return sb;
        }
    
        sb.append(rtrim(text.substring(0, pos))).append(defaultNewLine);
    }
