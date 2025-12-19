package edu.mokpo.sh_project.controller;

import edu.mokpo.sh_project.entity.GameHistory;
import edu.mokpo.sh_project.entity.Member;
import edu.mokpo.sh_project.repository.GameHistoryRepository;
import edu.mokpo.sh_project.service.AiGeminiService;
import jakarta.servlet.http.HttpSession;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;

import java.util.List;
import java.util.Map;

@Controller
@RequiredArgsConstructor
public class GameController {
    private final AiGeminiService aiGeminiService;
    private final GameHistoryRepository gameHistoryRepository;

    // [1] 시나리오 화면
    @GetMapping("/game/play")
    public String play(HttpSession session, Model model) {
        Member user = (Member) session.getAttribute("user");
        Integer day = (Integer) session.getAttribute("day");
        if (day == null) day = 1;

        Map<String, Object> scenario = aiGeminiService.getScenario(user.getPersona(), day, "");

        // 중요: 시나리오 제목을 세션에 저장 (나중에 DB 저장 시 사용)
        session.setAttribute("currentTitle", scenario.get("title"));

        model.addAttribute("scenario", scenario);
        model.addAttribute("nickname", user.getNickname());
        model.addAttribute("day", day);
        return "game";
    }

    // [2] 선택 제출 -> DB 1차 저장 (회고 제외)
    @PostMapping("/game/select")
    public String select(@RequestParam String choice, HttpSession session) {
        Member user = (Member) session.getAttribute("user");
        Integer day = (Integer) session.getAttribute("day");
        String title = (String) session.getAttribute("currentTitle");

        // 가상의 점수 계산 (실제로는 AI 서비스 활용 가능)
        GameHistory history = new GameHistory();
        history.setMember(user);
        history.setDay(day);
        history.setScenarioTitle(title);
        history.setUserChoice(choice);
        history.setScoreSelf(80); // 예시 점수

        gameHistoryRepository.save(history);

        return "redirect:/game/reflection";
    }

    // [3] 회고 페이지 이동
    @GetMapping("/game/reflection")
    public String reflectionPage(HttpSession session, Model model) {
        Member user = (Member) session.getAttribute("user");
        model.addAttribute("nickname", user.getNickname());
        model.addAttribute("day", session.getAttribute("day"));
        return "game/reflection";
    }

    // [4] 회고 저장 -> 다음날 또는 결과창
    @PostMapping("/game/reflection")
    public String saveReflection(@RequestParam String reflection, HttpSession session) {
        Member user = (Member) session.getAttribute("user");
        Integer day = (Integer) session.getAttribute("day");

        // 방금 저장한 기록에 회고 추가
        gameHistoryRepository.findFirstByMemberAndDayOrderByIdDesc(user, day).ifPresent(h -> {
            h.setReflection(reflection);
            gameHistoryRepository.save(h);
        });

        if (day >= 3) {
            return "redirect:/game/result";
        } else {
            session.setAttribute("day", day + 1);
            return "redirect:/game/play";
        }
    }

    // [5] 최종 결과 리포트
    @GetMapping("/game/result")
    public String result(HttpSession session, Model model) {
        Member user = (Member) session.getAttribute("user");
        List<GameHistory> histories = gameHistoryRepository.findByMemberId(user.getId());

        String analysis = aiGeminiService.getFinalAnalysis(histories.toString());

        model.addAttribute("nickname", user.getNickname());
        model.addAttribute("histories", histories);
        model.addAttribute("analysis", analysis);
        return "game/result";
    }
}