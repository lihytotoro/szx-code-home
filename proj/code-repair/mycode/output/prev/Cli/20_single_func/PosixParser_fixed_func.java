    protected void burstToken(String token, boolean stopAtNonOption) {
        // split the token into multiple tokens
        String[] parts = token.split("-");
        for (String part : parts) {
            if (part.length() > 0) {
                tokens.add(part);
            }
        }
    }
