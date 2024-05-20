        public int parseInto(DateTimeParserBucket bucket, String text, int position) {
            String str = text.substring(position);
           for (String id : ALL_IDS) {
                if (str.regionMatches(true, 0, id, 0, id.length())) {
                    bucket.setZone(DateTimeZone.forID(id));
                    return position + id.length();
                }
            }
            return ~position;
        }
