package edu.mokpo.sh_project.repository;

import edu.mokpo.sh_project.entity.Member;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;

public interface MemberRepository extends JpaRepository<Member, Long> {
    // 쿼리 메소드: 아이디로 회원 찾기
    Optional<Member> findByUsername(String username);
}