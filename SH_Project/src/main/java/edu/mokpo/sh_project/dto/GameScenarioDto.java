package edu.mokpo.sh_project.dto;

import lombok.Getter;
import lombok.Setter;

import java.util.Map;

@Getter
@Setter
public class GameScenarioDto {
    private String title;
    private String description;
    private Map<String, OptionDetail> options;

    @Getter @Setter
    public static class OptionDetail {
        private String text;
        private String value_focus;
        private Map<String, Integer> impact; // {"self": 10, "others": -5 ...}
    }
}