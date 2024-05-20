        final void newAttribute() {
            if (attributes == null)
                attributes = new Attributes();
            if (pendingAttributeName != null) {
                pendingAttributeName = pendingAttributeName.trim();
                   if (hasPendingAttributeValue)
                        attributes.put(new Attribute(pendingAttributeName,
                            pendingAttributeValue.length() > 0 ? pendingAttributeValue.toString() : pendingAttributeValueS));
                    else if (hasEmptyAttributeValue)
                        attributes.put(new Attribute(pendingAttributeName, ""));
                    else
                        attributes.put(new BooleanAttribute(pendingAttributeName));
            }
            pendingAttributeName = null;
            hasEmptyAttributeValue = false;
            hasPendingAttributeValue = false;
            reset(pendingAttributeValue);
            pendingAttributeValueS = null;
        }
