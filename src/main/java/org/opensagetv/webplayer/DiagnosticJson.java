package org.opensagetv.webplayer;

import java.util.regex.Pattern;

/** Bounded JSON grammar walk, not regex substitution across nested values.
 * Redacting a crypto object must consume the WHOLE value or the surrounding
 * diagnostic report becomes invalid JSON. No scripting engine/dependency. */
final class DiagnosticJson {
    private static final Pattern SECRET=Pattern.compile("(?i)(authorization|cookie|password|passwd|secret|token|credential|session.?key|crypto.*|private.?key|share.?user|share.?pass)");
    private static final Pattern CONTENT=Pattern.compile("(?i)(payload|subtitle.?text|caption.?text|media.?bytes|raw.?data|cue.?data)");
    private static final Pattern NUMBER=Pattern.compile("-?(?:0|[1-9][0-9]*)(?:\\.[0-9]+)?(?:[eE][+-]?[0-9]+)?");
    private final String input;private int cursor,values;
    private DiagnosticJson(String input){this.input=input;}
    static String sanitize(String raw,int limit){
        if(raw==null||raw.trim().isEmpty())return "null";
        if(raw.length()>limit)return "{\"unavailable\":\"Diagnostic JSON exceeds limit\"}";
        try{
            DiagnosticJson parser=new DiagnosticJson(raw);StringBuilder out=new StringBuilder(raw.length());parser.value(out,0);parser.space();
            if(parser.cursor!=raw.length())throw new IllegalArgumentException();return out.toString();
        }catch(IllegalArgumentException invalid){return "{\"unavailable\":\"Invalid diagnostic JSON\"}";}
    }
    private void space(){while(cursor<input.length()&&" \r\n\t".indexOf(input.charAt(cursor))>=0)cursor++;}
    private char take(){if(cursor>=input.length())throw new IllegalArgumentException();return input.charAt(cursor++);}
    private void expect(char expected){space();if(take()!=expected)throw new IllegalArgumentException();}
    private boolean next(char ch){space();if(cursor<input.length()&&input.charAt(cursor)==ch){cursor++;return true;}return false;}
    private void append(StringBuilder out,String value){if(out!=null)out.append(value);}
    private void quote(StringBuilder out,String value){if(out!=null)out.append('"').append(HttpUtil.json(value)).append('"');}
    private void value(StringBuilder out,int depth){
        if(depth>32||++values>65536)throw new IllegalArgumentException();space();if(cursor>=input.length())throw new IllegalArgumentException();
        char ch=input.charAt(cursor);
        if(ch=='{'){
            cursor++;append(out,"{");boolean first=true;
            if(!next('}'))do{
                if(!first)append(out,",");first=false;space();String key=string();expect(':');quote(out,key);append(out,":");
                String replacement=SECRET.matcher(key).matches()?"[redacted]":CONTENT.matcher(key).matches()?"[omitted-content]":null;
                if(replacement!=null){value(null,depth+1);quote(out,replacement);}else value(out,depth+1);
                if(next('}'))break;expect(',');
            }while(true);
            append(out,"}");return;
        }
        if(ch=='['){
            cursor++;append(out,"[");boolean first=true;
            if(!next(']'))do{if(!first)append(out,",");first=false;value(out,depth+1);if(next(']'))break;expect(',');}while(true);
            append(out,"]");return;
        }
        if(ch=='"'){quote(out,string());return;}
        for(String literal:new String[]{"null","true","false"})if(input.startsWith(literal,cursor)){cursor+=literal.length();append(out,literal);return;}
        int start=cursor;while(cursor<input.length()&&"-+0123456789.eE".indexOf(input.charAt(cursor))>=0)cursor++;
        String number=input.substring(start,cursor);if(!NUMBER.matcher(number).matches())throw new IllegalArgumentException();append(out,number);
    }
    private String string(){
        if(take()!='"')throw new IllegalArgumentException();StringBuilder out=new StringBuilder();
        while(true){char ch=take();if(ch=='"')return out.toString();if(ch<32)throw new IllegalArgumentException();
            if(ch!='\\'){out.append(ch);continue;}
            switch(take()){
                case '"':out.append('"');break;case '\\':out.append('\\');break;case '/':out.append('/');break;
                case 'b':out.append('\b');break;case 'f':out.append('\f');break;case 'n':out.append('\n');break;case 'r':out.append('\r');break;case 't':out.append('\t');break;
                case 'u':int code=0;for(int i=0;i<4;i++){int digit=Character.digit(take(),16);if(digit<0)throw new IllegalArgumentException();code=(code<<4)|digit;}out.append((char)code);break;
                default:throw new IllegalArgumentException();
            }
        }
    }
}
