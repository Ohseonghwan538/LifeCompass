package edu.mokpo.sh_project.dto;

import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class MemberDto {
    private String username;
    private String password;
    private String nickname;
    private String persona; // "20대 SW전공 대학생" 등
}