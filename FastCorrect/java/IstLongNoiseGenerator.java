import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONArray;
import com.alibaba.fastjson.JSONException;
import com.alibaba.fastjson.JSONObject;
import org.apache.commons.lang3.StringUtils;
import org.apache.http.HttpResponse;
import org.apache.http.client.HttpClient;
import org.apache.http.client.config.RequestConfig;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.ByteArrayEntity;
import org.apache.http.entity.ContentType;
import org.apache.http.entity.StringEntity;
import org.apache.http.impl.client.DefaultConnectionKeepAliveStrategy;
import org.apache.http.impl.client.HttpClientBuilder;
import org.apache.http.impl.conn.PoolingHttpClientConnectionManager;
import org.apache.http.util.EntityUtils;

import java.io.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * <p> TODO:add description here
 *
 * @author wanghongzhi
 * @date 2022/09/28
 */

public class IstLongNoiseGenerator {
    private static String corpusRootDir = "./sports_long_corpus1";
    private static String noisedCorpusDir = "./noised_sports_long_corpus1";

    private static String ttsUrl = "/lxy/api/tts/v1?AppId=hmf12yff&debug=true";
    private static String gatewayHttpAddress = "http://10.194.92.9:8080";

    private static String istUrl = "/lxy/api/ist/v1?AppId=hmf12yff&debug=true";

    private static ThreadLocal<String> istSid = new ThreadLocal<>();
    private static ThreadLocal<String> istResult = new ThreadLocal<>();

    private static ThreadLocal<Boolean> istEnded = new ThreadLocal<>();

    private static volatile AtomicInteger taskCounter = new AtomicInteger();

    private static volatile Map<String, Set<String>> istResultMap = new ConcurrentHashMap<>();

    private static final int MAX_NOISED = 5;

    private static final int MIN_SENTENCE_LEN = 2;

    private static HttpClient httpClient;

    private static final String seperatorChars = "<>。！!？?;；()（）[]【】{}「」—，,：";
    private static final String keepChars = "%@.*+-=/×÷~&、·':<>";
    private static final Set<Character> keepCharsSet = new TreeSet<>();
    private static final Set<Character> seperatorCharsSet = new TreeSet<>();
    static {
        for (Character ch : keepChars.toCharArray()) {
            keepCharsSet.add(ch);
        }
        for (Character ch : seperatorChars.toCharArray()) {
            seperatorCharsSet.add(ch);
        }
    }
    private static byte[] tts(String english, int speed) {
        String url = gatewayHttpAddress + ttsUrl;

        // 请求体
        Map<String, Object> sessionParam = new HashMap<>();
        sessionParam.put("sid", UUID.randomUUID().toString());
        sessionParam.put("audio_coding", "wav");
        sessionParam.put("sample_rate", "16000");
        //sessionParam.put("original_time", original_time);
        sessionParam.put("volume", "20");
        sessionParam.put("speed", String.valueOf(speed));
        sessionParam.put("pitch", "0");
        // sessionParam.put("native_voice_name", "aisCatherine");
        // sessionParam.put("native_voice_name", "bingjie");
        sessionParam.put("native_voice_name", "xiaozhou");

        try {
            return IstLongNoiseGenerator.sendTTSReqAndGetRes(url, sessionParam, english);
        } catch (Exception e) {
            System.err.println("failed to send tts request:");
            e.printStackTrace();
        }
        return null;
    }

    private static void initHttpClient() {
        // 生成默认请求配置
        RequestConfig.Builder requestConfigBuilder = RequestConfig.custom();
        // 超时时间
        requestConfigBuilder.setSocketTimeout(5 * 1000);
        // 连接时间
        requestConfigBuilder.setConnectTimeout(5 * 1000);

        requestConfigBuilder.setConnectionRequestTimeout(5 * 1000);

        RequestConfig defaultRequestConfig = requestConfigBuilder.build();
        // 连接池配置
        // 长连接保持30秒
        final PoolingHttpClientConnectionManager pollingConnectionManager = new PoolingHttpClientConnectionManager
                (-1, TimeUnit.SECONDS);
        // 总连接数
        pollingConnectionManager.setMaxTotal(1000);
        // 同路由的并发数
        pollingConnectionManager.setDefaultMaxPerRoute(1000);

        // httpclient 配置
        HttpClientBuilder httpClientBuilder = HttpClientBuilder.create();
        // 保持长连接配置，需要在头添加Keep-Alive
        httpClientBuilder.setKeepAliveStrategy(new DefaultConnectionKeepAliveStrategy());
        httpClientBuilder.setConnectionManager(pollingConnectionManager);
        httpClientBuilder.setDefaultRequestConfig(defaultRequestConfig);
        httpClient = httpClientBuilder.build();
    }

    public static byte[] sendTTSReqAndGetRes(String url, Map<String, Object> sessionParam,
                                             String text) throws Exception {
        String sessionParamBase64 = Base64.getEncoder().encodeToString(JSONObject.toJSONString(sessionParam).getBytes());

        Map<String, String> bodyMap = new HashMap<>();
        bodyMap.put("text", text);

        HttpPost httpPost = new HttpPost(url);
        httpPost.setHeader("sid", UUID.randomUUID().toString());
        httpPost.setHeader("Content-Type", "application/json");
        httpPost.setHeader("sessionParam", sessionParamBase64);
        httpPost.setEntity(new StringEntity(JSON.toJSONString(bodyMap), "UTF-8"));
        //发送HTTP请求
        HttpResponse httpResponse = httpClient.execute(httpPost);
        if (httpResponse.getEntity().getContentType().getValue().contains("json")) {
            return null;
        } else {
            byte[] bytes = EntityUtils.toByteArray(httpResponse.getEntity());
//            File file = new File("c:/audios/16000.wav");
//            if (file.exists()) {
//                boolean isDeleteSuccess = file.delete();
//                if (!isDeleteSuccess) {
//                    System.err.println("原文件存在，无法删除");
//                }
//            }
//            FileOutputStream fos = new FileOutputStream(file);
//            fos.write(bytes);
//            fos.flush();
//            fos.close();

            return bytes;
        }
    }

    private static void saveProcessedFilePath(String filePath) {
        String processedFilePath = "./.processed.txt";
        BufferedWriter writer = null;
        try {
            writer = new BufferedWriter(new OutputStreamWriter(new FileOutputStream(processedFilePath, true)));
            writer.write(filePath + "\n");
            writer.close();
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        } finally {
            if (writer != null) {
                try {
                    writer.close();
                } catch (Exception e) {}
            }
        }
    }
    private static Set<String> loadProcessedFilePaths() {
        String processedFilePath = "./.processed.txt";
        Set<String> processedFiles = new TreeSet<>();
        File processedFile = new File(processedFilePath);
        if (!processedFile.exists()) {
            return processedFiles;
        }

        try {
            BufferedReader reader = new BufferedReader(new FileReader(processedFilePath));
            String line;
            for(line = reader.readLine(); line != null; line = reader.readLine()) {
                processedFiles.add(line);
            }
            reader.close();
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        }
        return processedFiles;
    }

    private static String ist(String text, byte[] audioBytes) throws Exception {
        istResult.set(new String());
        String uuid = UUID.randomUUID().toString(); // 一个文件不同线程共用相同的sid
        istSid.set(uuid);
        istEnded.set(false);

        Map<String, String> sessionParam = new HashMap<>();
        sessionParam.put("rate", "16k");
        sessionParam.put("rst", "json");
        sessionParam.put("aue", "raw");
        sessionParam.put("rse", "utf8");
        sessionParam.put("bos", "600000");
        sessionParam.put("eos", "600000");
        sessionParam.put("language", "ch16");
        sessionParam.put("catCode", "football");
        sessionParam.put("errorCorrectionFlag", "0");
        JSONObject liveParam = new JSONObject();
        liveParam.put("liveId", "111");
        liveParam.put("catCode", "football");
        sessionParam.put("liveParam", liveParam.toString());

        int sliceSize = 20480;
        byte[] sliceBytes = new byte[sliceSize];
        int sliceNum = (int) Math.ceil((double) audioBytes.length / sliceSize);
        for(int i = 0; i < sliceNum-1; i++) {
            System.arraycopy(audioBytes, i*sliceSize, sliceBytes, 0, sliceSize);
            sendIstReq(text, sliceNum, String.valueOf(i+1), sessionParam, sliceBytes, 0);
            if(istEnded.get()) {
                break;
            }
        }
        if(!istEnded.get()) {
            int remainBytesLen = audioBytes.length - (sliceNum - 1) * sliceSize;
            byte[] remainBytes = new byte[remainBytesLen];
            System.arraycopy(audioBytes, (sliceNum - 1) * sliceSize, remainBytes, 0, remainBytesLen);
            sendIstReq(text, sliceNum, String.valueOf(sliceNum), sessionParam, remainBytes, 1);
        }
        return istResult.get();
    }
    private static void sendIstReq(String text, int sliceNum, String number, Map<String, String> sessionParam,
                                   byte[] audioBytes, int endFlag) throws Exception {
        if(istEnded.get()) {
            return;
        }
        // System.out.println("begin to send " + number + " slice");
        String url = gatewayHttpAddress + istUrl;
        HttpPost httpPost = new HttpPost(url);
        String sessionParamBase64 = null;
        if (sessionParam != null) {
            sessionParamBase64 = Base64.getEncoder().encodeToString(JSON.toJSONString(sessionParam).getBytes());
        }
        httpPost.setHeader("sid", istSid.get());
        // System.out.println(Thread.currentThread().getName() + ": iat sid=" + iatSid.get() + ", number="+number);
        httpPost.setHeader("Content-Type", "application/json");
        httpPost.setHeader("sessionParam", sessionParamBase64);
        httpPost.setHeader("endFlag", String.valueOf(endFlag));
        httpPost.setHeader("number", String.valueOf(number));

        // 设置HTTP数据
        httpPost.setEntity(new ByteArrayEntity(audioBytes, ContentType.APPLICATION_OCTET_STREAM));

        //发送HTTP请求
        HttpResponse httpResponse = httpClient.execute(httpPost);
        String response = EntityUtils.toString(httpResponse.getEntity());
        JSONObject jsonObject = JSONObject.parseObject(response);
        if (!jsonObject.containsKey("body")) {
            System.err.println(": ist failed: " + response + ", istResult="+ istResult.get());
            // throw new Exception(response);
        } else if (jsonObject.containsKey("body") && (jsonObject.get("body") != null && jsonObject.getJSONArray(
                "body").size() > 0)) {
            // System.err.println(Thread.currentThread().getName() + ": iat succeed: ");

            JSONArray body = jsonObject.getJSONArray("body");
            StringBuilder sbResult = new StringBuilder();
            for (int idx = 0; idx < body.size(); idx++) {
                String end = body.getJSONObject(idx).getString("endFlag");
                if ("true".equals(end)) {
                    istEnded.set(true);
                }

                JSONObject frameResult = body.getJSONObject(idx);
                String ansStr = frameResult.getString("ansStr"); //ansStr还是ws_s???
                if (ansStr != null && ansStr.length() > 0) {
                    try {
                        JSONObject ansStrJson = JSONObject.parseObject(ansStr);
                        String origText = ansStrJson.getString("ws_origin");
                        if(StringUtils.isBlank(origText)) {
                            return;
                        }

                        JSONObject origJson = JSONObject.parseObject(origText);
                        JSONArray rt = origJson.getJSONObject("cn").getJSONObject("st").getJSONArray("rt");
                        for (int k = 0; k < rt.size(); k++) {
                            JSONArray ws = rt.getJSONObject(k).getJSONArray("ws");
                            if(ws == null || ws.size() == 0) {
                                return;
                            }
                            for (int i = 0; i < ws.size(); i++) {
                                JSONArray cw = ws.getJSONObject(i).getJSONArray("cw");
                                for (int j = 0; j < cw.size(); j++) {
                                    String w = cw.getJSONObject(j).getString("w");
                                    for (char ch : w.toCharArray()) {
                                        if (('0' <= ch && ch <= '9') || ('\u4e00' <= ch && ch <= '\u9fa5') || keepCharsSet.contains(ch)
                                                 || seperatorCharsSet.contains(ch) || ('A' <= ch && ch <= 'Z') || ('a' <= ch && ch <= 'z')) {
                                            sbResult.append(ch);
                                        }
                                    }
                                }
                            }
                        }
                        // System.out.println(stringBuilder.toString());
                    } catch (JSONException e) {
                        // System.out.println(ansStr);
                        System.err.println("exception occurs in parse result:");
                        e.printStackTrace();
                    }
                }
            }
            istResult.set(istResult.get() + sbResult);
        }
        if(istEnded.get() && endFlag == 0) {
            System.err.println("sid="+ istSid.get() + ", ratio=" + number + " / " + String.valueOf(sliceNum) + ", some audit bytes need to sent, text=" + text + ", istResult="+istResult.get());
        }
    }

    private static void task(String text) {
        Set<String> istResultSet = Collections.synchronizedSet(new TreeSet<>());
        for(int speed = -500; speed <= 500; speed += 250) {
            int count = 0;
            text = text.replaceAll(",", "，");
            String beginStr = text.substring(0, 1);
            if ("，".equals(beginStr) || ".".equals(beginStr)) {
                text = text.substring(1);
            }
            String endStr = text.substring(text.length() - 1);
            if ("，".equals(endStr) || ".".equals(beginStr)) {
                text = text.substring(0, text.length() - 1);
            }
            if (text.length() < MIN_SENTENCE_LEN) {
                return;
            }

            byte[] audioBytes = tts(text, speed);
            while (istResultSet.size() < MAX_NOISED && count < 4 && audioBytes == null) {
                audioBytes = tts(text, speed);
                count += 1;
            }
            if (audioBytes == null) {
                System.err.println("failed to do tts for: " + text + " at speed: " + speed);
                continue;
            }

            count = 0;
            while (count < 2) {
                try {
                    String istResult = ist(text, audioBytes);
                    if ((istResult != null) && (istResult.length() >= MIN_SENTENCE_LEN)) {
                        istResultSet.add(istResult);
                        // System.out.println(istResult);
                        break;
                    }
                } catch (Exception e) {
                    System.err.println("exception occurs in iat:");
                    e.printStackTrace();
                }
                count += 1;
            }
        }
        Set<String> oldIstResultSet = istResultMap.computeIfAbsent(text, k -> {return istResultSet;});
        if(oldIstResultSet != istResultSet) {
            oldIstResultSet.addAll(istResultSet);
        }
//        for(String pair : istResultMap.get(text)) {
//            System.out.println(text + " => " + pair);
//        }
    }

    private static void getCorpusFilePaths(File file, List<String> paths) {
        File flist[] = file.listFiles();
        if (flist == null || flist.length == 0) {
            return;
        }
        for (File f : flist) {
            if (f.isDirectory()) {
                getCorpusFilePaths(f, paths);
            } else {
                String path = f.getAbsolutePath();
                if(path.indexOf("世界杯") == -1 && path.indexOf("五大联赛") == -1) {
                    continue; //跳过非足球语料
                }
                paths.add(path);
            }
        }
    }

    private static void createDir(File file) {
        File parentFile = file.getParentFile();
        List<String> subPaths = new LinkedList<>();
        while(!parentFile.isDirectory()) {
            subPaths.add(parentFile.getName());
            parentFile = parentFile.getParentFile();
        }
        String fullPath = parentFile.getAbsolutePath();
        for(int idx = subPaths.size() -1; idx >= 0; idx--) {
            fullPath += ("/" + subPaths.get(idx));
            File subPathFile = new File(fullPath);
            subPathFile.mkdir();
        }
    }

    public static void main(String[] args) throws Exception {
        initHttpClient();
        List<String> corpusFilePathList = new LinkedList<>();
        File rootDirFile = new File(corpusRootDir);
        File outputRootDirFile = new File(noisedCorpusDir);
        getCorpusFilePaths(rootDirFile, corpusFilePathList);
        Set<String> processedFilePaths = loadProcessedFilePaths();
        System.out.println(processedFilePaths.size() + " files already processed.");

        BlockingQueue<Runnable> taskQueue = new LinkedBlockingQueue<Runnable>();
        ExecutorService es = new ThreadPoolExecutor(60, 60, 60L,
                TimeUnit.SECONDS, taskQueue);

        File outputDir = new File(noisedCorpusDir);
        if(!outputDir.exists()) {
            outputDir.mkdir();
        }

        int processedCorpusFiles = 0;
        for(String corpusFilePath : corpusFilePathList) {
            if(processedFilePaths.contains(corpusFilePath)) { //已经处理过的语料文件，跳过
                continue;
            }

            istResultMap = new ConcurrentHashMap<>();
            taskCounter = new AtomicInteger();
            try {
                BufferedReader reader = new BufferedReader(new FileReader(corpusFilePath));
                String line;
                for(line = reader.readLine(); line != null; line = reader.readLine()) {
                    if(line.length() < MIN_SENTENCE_LEN) {
                        continue;
                    }

                    String corpus = line;
                    es.submit(() -> {
                        try {
                            task(corpus);
                        } catch (Exception e) {
                            System.err.println("error occurs while process corpus: " + corpus);
                            e.printStackTrace();
                        } finally {
                            taskCounter.decrementAndGet();
                        }
                    });
                    taskCounter.incrementAndGet();
                }
                reader.close();
            } catch (Exception e) {
                System.err.println("error occurs while process corpus file: " + corpusFilePath);
            }
            while (taskCounter.get() > 0) {
                Thread.sleep(100);
            }
            BufferedWriter writer = null;
            String outputFilePath = outputRootDirFile.getAbsolutePath() + "/" + corpusFilePath.substring(rootDirFile.getAbsolutePath().length());
            if(outputFilePath.endsWith(".txt")) {
                outputFilePath = outputFilePath.substring(0, outputFilePath.length() - 4) + "_asr.txt";
            }
            File outputFile = new File(outputFilePath);
            createDir(outputFile);
            if(outputFile.exists()) {
                System.out.println("former noised corpus file: " + outputFilePath + " find, overwrite it.");
            }
            try {
                writer = new BufferedWriter(new OutputStreamWriter(new FileOutputStream(outputFilePath, false)));
                for(String corpus : istResultMap.keySet()) {
                    for(String istResult : istResultMap.getOrDefault(corpus, new TreeSet<>())) {
                        String line = corpus.trim() + "\t" + istResult + "\n";
                        writer.write(line);
                    }
                }
            } catch (Exception e) {
                System.err.println("failed to create noised corpus file:" + outputFilePath);
                continue;
            } finally {
                if(writer != null) {
                    writer.close();
                }
            }
            processedCorpusFiles += 1;
            saveProcessedFilePath(corpusFilePath);
            float ratio0 = processedCorpusFiles *100.0f / corpusFilePathList.size();
            int ratio = (int)ratio0;
            System.out.println(ratio + "% (" + processedCorpusFiles + "/" + corpusFilePathList.size()  + ") files processed.");
        }
        es.shutdownNow();
    }
}
