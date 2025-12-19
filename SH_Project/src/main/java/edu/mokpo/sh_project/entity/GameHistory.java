package edu.mokpo.sh_project.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

@Entity
@Getter
@Setter
public class GameHistory {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne
    private Member member;

    private int day;
    private String scenarioTitle; // 시나리오 제목 저장
    private String userChoice;    // 사용자의 선택 텍스트

    @Column(columnDefinition = "TEXT")
    private String reflection;    // 사용자의 회고 답변

    // 점수 필드들
    private int scoreSelf;
    private int scoreOthers;
    private int scoreWorld;
    private int scoreAttitude;
}