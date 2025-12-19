package edu.mokpo.sh_project.service;

import edu.mokpo.sh_project.dto.MemberDto;
import edu.mokpo.sh_project.entity.Member;
import edu.mokpo.sh_project.repository.MemberRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

//(회원관리 필수 기능 구현)
@Service
@RequiredArgsConstructor
public class MemberService {
    private final MemberRepository memberRepository;

    public void join(MemberDto dto) {
        Member member = new Member();
        member.setUsername(dto.getUsername());
        member.setPassword(dto.getPassword()); // 실제론 암호화 필요
        member.setNickname(dto.getNickname());
        member.setPersona(dto.getPersona());
        memberRepository.save(member);
    }

    // 삭제, 수정 기능 추가 구현 필요
}