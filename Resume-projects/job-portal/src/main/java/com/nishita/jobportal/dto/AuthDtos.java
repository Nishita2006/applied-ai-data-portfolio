package com.nishita.jobportal.dto;
import com.nishita.jobportal.entity.Role;
import jakarta.validation.constraints.*;
public final class AuthDtos {
 private AuthDtos(){}
 public record RegisterRequest(@NotBlank String name,@Email @NotBlank String email,@Size(min=8,max=72) String password,@NotNull Role role){}
 public record LoginRequest(@Email @NotBlank String email,@NotBlank String password){}
 public record AuthResponse(String token,Long userId,String name,String email,Role role){}
}
