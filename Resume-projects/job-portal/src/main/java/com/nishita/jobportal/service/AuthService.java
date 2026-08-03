package com.nishita.jobportal.service;
import com.nishita.jobportal.dto.AuthDtos.*;
import com.nishita.jobportal.entity.*;
import com.nishita.jobportal.exception.ConflictException;
import com.nishita.jobportal.repository.*;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.authentication.*;
import org.springframework.security.core.Authentication;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.oauth2.jwt.*;
import org.springframework.security.oauth2.jose.jws.MacAlgorithm;
import org.springframework.stereotype.Service;
import java.time.*;
import java.util.List;
@Service public class AuthService{
 private final UserRepository users; private final CandidateProfileRepository profiles; private final PasswordEncoder encoder; private final AuthenticationManager authenticationManager; private final JwtEncoder jwtEncoder;
 @Value("${app.jwt-hours}") private long jwtHours;
 public AuthService(UserRepository u,CandidateProfileRepository p,PasswordEncoder e,AuthenticationManager a,JwtEncoder j){users=u;profiles=p;encoder=e;authenticationManager=a;jwtEncoder=j;}
 public AuthResponse register(RegisterRequest r){if(users.existsByEmailIgnoreCase(r.email()))throw new ConflictException("An account already exists for this email");UserAccount u=new UserAccount();u.setName(r.name().trim());u.setEmail(r.email().trim().toLowerCase());u.setPasswordHash(encoder.encode(r.password()));u.setRole(r.role());u=users.save(u);if(u.getRole()==Role.CANDIDATE){CandidateProfile p=new CandidateProfile();p.setUser(u);profiles.save(p);}return issue(u);}
 public AuthResponse login(LoginRequest r){Authentication auth=authenticationManager.authenticate(new UsernamePasswordAuthenticationToken(r.email().toLowerCase(),r.password()));UserAccount u=users.findByEmailIgnoreCase(auth.getName()).orElseThrow();return issue(u);}
 private AuthResponse issue(UserAccount u){Instant now=Instant.now();JwtClaimsSet claims=JwtClaimsSet.builder().issuer("job-portal").issuedAt(now).expiresAt(now.plus(Duration.ofHours(jwtHours))).subject(u.getEmail()).claim("roles",List.of(u.getRole().name())).claim("userId",u.getId()).build();JwsHeader header=JwsHeader.with(MacAlgorithm.HS256).build();String token=jwtEncoder.encode(JwtEncoderParameters.from(header,claims)).getTokenValue();return new AuthResponse(token,u.getId(),u.getName(),u.getEmail(),u.getRole());}
}
