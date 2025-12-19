package edu.mokpo.sh_project.repository;

import edu.mokpo.sh_project.entity.GameHistory;
import edu.mokpo.sh_project.entity.Member;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.Optional;

// GameHistoryRepository.java
public interface GameHistoryRepository extends JpaRepository<GameHistory, Long> {

    // Member와 Day가 일치하는 데이터 중 가장 최근(ID가 큰 것) 하나만 가져옴
    Optional<GameHistory> findFirstByMemberAndDayOrderByIdDesc(Member member, int day);

    List<GameHistory> findByMemberId(Long memberId);
}