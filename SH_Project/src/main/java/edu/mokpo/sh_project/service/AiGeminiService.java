package edu.mokpo.sh_project.service;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.*;

@Service
@Slf4j
public class AiGeminiService {
    @Value("${gemini.api.key}")
    private String apiKey;

    private final String API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=";
    private final RestTemplate restTemplate = new RestTemplate();
    private final ObjectMapper objectMapper = new ObjectMapper();

    // 1. 시나리오 생성 로직
    public Map<String, Object> getScenario(String persona, int day, String history) {
        String prompt = String.format(
                "너는 윤리 게임 설계자야. 아래 JSON 형식으로만 대답해. 다른 말은 절대 하지 마.\n" +
                        "대상 페르소나: %s, 진행: %d일차.\n" +
                        "응답 형식: {\"title\": \"제목\", \"content\": \"내용\", \"optionA\": \"선택지1\", \"optionB\": \"선택지2\", \"optionC\": \"선택지3\"}",
                persona, day
        );

        // 이전에 드린 callAiAndParseJson 메서드를 사용하여 반환
        return callAiAndParseJson(prompt);
    }

    // 2. 종합 분석 로직
    public String getFinalAnalysis(String summary) {
        String prompt = summary + " 위 기록을 보고 이 사용자의 윤리적 가치관을 분석해 주세요. (한국어)";
        return callAiAndGetText(prompt);
    }

    // [Helper] JSON 파싱 및 에러 방어
    private Map<String, Object> callAiAndParseJson(String prompt) {
        try {
            String response = callAi(prompt);
            String jsonText = extractJson(response);
            return objectMapper.readValue(jsonText, Map.class);
        } catch (Exception e) {
            log.error("JSON 파싱 에러: {}", e.getMessage());
            return Map.of("title", "에러", "content", "다시 시도", "optionA", "확인", "optionB", "확인", "optionC", "확인");
        }
    }

    private String callAi(String prompt) {
        Map<String, Object> body = Map.of("contents", List.of(Map.of("parts", List.of(Map.of("text", prompt)))));
        return restTemplate.postForObject(API_URL + apiKey, body, String.class);
    }

    private String extractJson(String rawResponse) throws Exception {
        JsonNode root = objectMapper.readTree(rawResponse);
        String text = root.path("candidates").get(0).path("content").path("parts").get(0).path("text").asText();
        return text.replaceAll("```json|```", "").trim();
    }

    private String callAiAndGetText(String prompt) {
        try {
            JsonNode root = objectMapper.readTree(callAi(prompt));
            return root.path("candidates").get(0).path("content").path("parts").get(0).path("text").asText();
        } catch (Exception e) { return "분석 불가"; }
    }
}