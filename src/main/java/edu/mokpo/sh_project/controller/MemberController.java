package edu.mokpo.sh_project.controller;

import edu.mokpo.sh_project.entity.Member;
import edu.mokpo.sh_project.repository.MemberRepository;
import jakarta.servlet.http.HttpSession;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;

import java.util.Optional;

@Slf4j
@Controller
@RequiredArgsConstructor
public class MemberController {

    private final MemberRepository memberRepository;

    // 로그인 페이지 표시
    @GetMapping("/login")
    public String loginPage() {
        return "login";
    }

    // 로그인 로직 처리
    @PostMapping("/login")
    public String login(@RequestParam String username,
                        @RequestParam String password,
                        HttpSession session,
                        Model model) {

        log.info("로그인 시도: {}", username);

        // 1. DB에서 해당 아이디의 사용자 조회
        Optional<Member> member = memberRepository.findByUsername(username);

        // 2. 사용자 존재 및 비밀번호 일치 확인 (간단 구현)
        if (member.isPresent() && member.get().getPassword().equals(password)) {
            // 로그인 성공 시 세션에 저장
            session.setAttribute("user", member.get());
            session.setAttribute("day", 1); // 게임 시작일 초기화
            log.info("로그인 성공: {}", username);
            return "redirect:/game/play"; // 게임 화면으로 이동
        } else {
            // 로그인 실패
            log.warn("로그인 실패: {}", username);
            model.addAttribute("error", "아이디 또는 비밀번호가 일치하지 않습니다.");
            return "login";
        }
    }

    // 로그아웃
    @GetMapping("/logout")
    public String logout(HttpSession session) {
        session.invalidate();
        return "redirect:/login";
    }

    // MemberController.java에 추가

    // 회원가입 페이지 이동
    @GetMapping("/join")
    public String joinPage() {
        return "join";
    }

    // 회원가입 데이터 처리
    @PostMapping("/join")
    public String join(@RequestParam String username,
                       @RequestParam String password,
                       @RequestParam String nickname,
                       @RequestParam String persona) {

        log.info("회원가입 시도: {}", username);

        // 1. 새로운 Member 엔티티 생성
        Member newMember = new Member();
        newMember.setUsername(username);
        newMember.setPassword(password); // 프로젝트 수준이므로 평문 저장 (보안상 원래는 암호화 필요)
        newMember.setNickname(nickname);
        newMember.setPersona(persona);

        // 2. DB 저장
        try {
            memberRepository.save(newMember);
            log.info("회원가입 완료: {}", username);
        } catch (Exception e) {
            log.error("회원가입 실패: {}", e.getMessage());
            return "redirect:/join?error"; // 중복 아이디 등의 경우 가입 페이지 재시도
        }

        // 3. 가입 완료 후 로그인 페이지로 리다이렉트
        return "redirect:/login";
    }
}