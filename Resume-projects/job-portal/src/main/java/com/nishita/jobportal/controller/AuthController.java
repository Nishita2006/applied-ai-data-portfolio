package com.nishita.jobportal.controller;
import com.nishita.jobportal.dto.AuthDtos.*;
import com.nishita.jobportal.service.AuthService;
import jakarta.validation.Valid;
import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;
@RestController @RequestMapping("/api/auth") public class AuthController{
 private final AuthService auth; public AuthController(AuthService a){auth=a;}
 @PostMapping("/register") ResponseEntity<AuthResponse> register(@Valid @RequestBody RegisterRequest r){return ResponseEntity.status(HttpStatus.CREATED).body(auth.register(r));}
 @PostMapping("/login") AuthResponse login(@Valid @RequestBody LoginRequest r){return auth.login(r);}
}
