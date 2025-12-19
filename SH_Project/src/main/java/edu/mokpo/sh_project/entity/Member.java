package edu.mokpo.sh_project.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
import java.util.ArrayList;
import java.util.List;

@Entity
@Getter
@Setter
public class Member {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(unique = true, nullable = false)
    private String username; // 학번 또는 ID

    @Column(nullable = false)
    private String password;

    private String nickname;

    @Column(length = 1000)
    private String persona; // AI 시나리오의 기초가 되는 사용자 성격

    // 한 명의 회원은 여러 개의 게임 기록을 가질 수 있음
    @OneToMany(mappedBy = "member", cascade = CascadeType.ALL)
    private List<GameHistory> histories = new ArrayList<>();
}